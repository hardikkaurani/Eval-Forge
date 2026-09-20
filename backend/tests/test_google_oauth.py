import base64
import json
import secrets
import time
import uuid
from unittest.mock import AsyncMock, patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient
from jwt.algorithms import RSAAlgorithm
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import settings
from app.enterprise.exceptions import (
    OAuthConfigurationException,
    OAuthConflictException,
    OAuthStateInvalidException,
    OAuthVerificationException,
)
from app.enterprise.models import Membership, OAuthIdentity
from app.enterprise.services.google_oauth_service import (
    GoogleOAuthService,
    is_safe_redirect_url,
)
from app.main import app

TEST_CLIENT_ID = "test-google-client-id-12345.apps.googleusercontent.com"
TEST_CLIENT_SECRET = "GOCSPX-test-very-secret-value-never-leak"
TEST_REDIRECT_URI = "http://localhost:8000/api/v1/auth/google/callback"


@pytest.fixture(scope="module")
def rsa_keypair():
    """Generates an RSA keypair and matching JWK for testing ID token validation."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk_dict = json.loads(RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk_dict["kid"] = "evalforge-test-key-1"
    jwk_dict["alg"] = "RS256"
    jwk_dict["use"] = "sig"
    return private_key, jwk_dict


@pytest.fixture
def make_id_token(rsa_keypair):
    """Factory creating signed JWT ID tokens with customizable claims."""
    private_key, jwk_dict = rsa_keypair

    def _maker(
        sub: str = "google-sub-10001",
        email: str = "evalforge.user@example.com",
        email_verified: bool = True,
        aud: str = TEST_CLIENT_ID,
        iss: str = "https://accounts.google.com",
        exp_offset: int = 3600,
        nonce: str = None,
        name: str = "EvalForge Test User",
        picture: str = "https://example.com/avatar.jpg",
        kid: str = "evalforge-test-key-1",
    ) -> str:
        claims = {
            "sub": sub,
            "email": email,
            "email_verified": email_verified,
            "aud": aud,
            "iss": iss,
            "exp": int(time.time()) + exp_offset,
            "iat": int(time.time()),
            "name": name,
            "picture": picture,
        }
        if nonce is not None:
            claims["nonce"] = nonce
        headers = {"kid": kid, "alg": "RS256"}
        return jwt.encode(claims, private_key, algorithm="RS256", headers=headers)

    return _maker


@pytest.fixture
def oauth_service(rsa_keypair):
    """GoogleOAuthService instance configured with test credentials and custom test JWKS."""
    _, jwk_dict = rsa_keypair
    svc = GoogleOAuthService(
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        redirect_uri=TEST_REDIRECT_URI,
        frontend_url="http://localhost:5173",
    )
    # Prime JWKS cache with test key
    svc._jwks_cache = {"keys": [jwk_dict], "expires_at": time.time() + 3600}
    return svc


# ==============================================================================
# 1. Configuration & Initial State Tests
# ==============================================================================


def test_01_oauth_configured_check():
    """Verify is_configured returns True only with all credentials present."""
    svc = GoogleOAuthService(
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        redirect_uri=TEST_REDIRECT_URI,
    )
    assert svc.is_configured() is True

    unconfigured = GoogleOAuthService(client_id="", client_secret="", redirect_uri="")
    assert unconfigured.is_configured() is False


def test_02_oauth_start_unconfigured_rejection():
    """Verify generate_auth_flow raises OAuthConfigurationException when credentials missing."""
    svc = GoogleOAuthService(client_id=None, client_secret=None, redirect_uri=None)
    with pytest.raises(OAuthConfigurationException):
        import asyncio

        asyncio.run(svc.generate_auth_flow())


# ==============================================================================
# 2. State CSRF & Nonce Validation Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_03_oauth_start_generates_valid_flow(oauth_service):
    """Verify generate_auth_flow creates proper authorization URL, state token, and nonce."""
    flow = await oauth_service.generate_auth_flow(return_to="/projects/123")
    assert "auth_url" in flow
    assert "state" in flow
    assert "nonce" in flow
    assert TEST_CLIENT_ID in flow["auth_url"]
    assert flow["state"] in flow["auth_url"]
    assert "response_type=code" in flow["auth_url"]


@pytest.mark.asyncio
async def test_04_attack_1_invalid_state_rejected(oauth_service):
    """ATTACK 1: Tampered or forged state signature must be rejected."""
    flow = await oauth_service.generate_auth_flow(return_to="/overview")
    valid_state = flow["state"]
    tampered_state = valid_state[:-4] + "dead"

    with pytest.raises(
        OAuthStateInvalidException, match="signature verification failed"
    ):
        await oauth_service.validate_state(tampered_state)

    with pytest.raises(OAuthStateInvalidException, match="Missing or invalid"):
        await oauth_service.validate_state("")


@pytest.mark.asyncio
async def test_05_attack_2_reused_state_rejected(oauth_service):
    """ATTACK 2: Replay attack with previously consumed state token must be rejected."""
    flow = await oauth_service.generate_auth_flow(return_to="/overview")
    state = flow["state"]

    # First consumption succeeds
    payload = await oauth_service.validate_state(state)
    assert payload["return_to"] == "/overview"

    # Second consumption must fail (single-use enforcement)
    with pytest.raises(OAuthStateInvalidException, match="already been used"):
        await oauth_service.validate_state(state)


@pytest.mark.asyncio
async def test_06_attack_3_expired_state_rejected(oauth_service):
    """ATTACK 3: State token past its 10-minute expiration window must be rejected."""
    nonce = secrets.token_hex(16)
    expired_exp = int(time.time()) - 60  # expired 1 minute ago
    payload = {"nonce": nonce, "exp": expired_exp, "return_to": "/overview"}
    raw = json.dumps(payload, sort_keys=True)
    b64 = base64.urlsafe_b64encode(raw.encode()).decode()
    import hashlib
    import hmac

    sig = hmac.new(
        oauth_service.secret_key.encode(), b64.encode(), hashlib.sha256
    ).hexdigest()
    expired_token = f"{b64}.{sig}"
    # Seed into memory
    oauth_service._memory_state_cache[
        f"oauth_state:{hashlib.sha256(expired_token.encode()).hexdigest()}"
    ] = float(expired_exp)

    with pytest.raises(OAuthStateInvalidException, match="expired"):
        await oauth_service.validate_state(expired_token)


# ==============================================================================
# 3. Open Redirect Protection Tests
# ==============================================================================


def test_07_open_redirect_safe_paths():
    """Verify internal relative paths are permitted."""
    allowed = ["http://localhost:5173"]
    assert is_safe_redirect_url("/overview", allowed) is True
    assert is_safe_redirect_url("/projects/abc-123?filter=all", allowed) is True
    assert is_safe_redirect_url("/settings/billing", allowed) is True
    assert is_safe_redirect_url("http://localhost:5173/overview", allowed) is True


def test_08_attack_8_external_redirect_rejected():
    """ATTACK 8: External domain redirects must be rejected."""
    allowed = ["http://localhost:5173"]
    assert is_safe_redirect_url("https://evil.example", allowed) is False
    assert is_safe_redirect_url("https://evil.com/phishing", allowed) is False
    assert is_safe_redirect_url("http://attacker.com", allowed) is False


def test_09_attack_8_protocol_relative_and_crlf_rejected():
    """ATTACK 8: Protocol-relative, backslash, and header-injection URLs must be rejected."""
    allowed = ["http://localhost:5173"]
    assert is_safe_redirect_url("//evil.com", allowed) is False
    assert is_safe_redirect_url("/\\evil.com", allowed) is False
    assert is_safe_redirect_url("\\\\evil.com", allowed) is False
    assert is_safe_redirect_url("/overview\r\nSet-Cookie: evil=1", allowed) is False
    assert is_safe_redirect_url("javascript:alert(1)", allowed) is False
    assert is_safe_redirect_url("data:text/html,evil", allowed) is False


# ==============================================================================
# 4. ID Token Verification & Attack Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_10_valid_id_token_verification(oauth_service, make_id_token):
    """Verify valid Google ID token passes verification and returns claims."""
    token = make_id_token(nonce="test-nonce-123")
    claims = await oauth_service.verify_id_token(token, expected_nonce="test-nonce-123")
    assert claims["sub"] == "google-sub-10001"
    assert claims["email"] == "evalforge.user@example.com"
    assert claims["email_verified"] is True


@pytest.mark.asyncio
async def test_11_attack_4_wrong_audience_rejected(oauth_service, make_id_token):
    """ATTACK 4: ID token minted for a different client application must be rejected."""
    token = make_id_token(aud="attacker-client-id-666.apps.googleusercontent.com")
    with pytest.raises(OAuthVerificationException, match="audience does not match"):
        await oauth_service.verify_id_token(token)


@pytest.mark.asyncio
async def test_12_attack_5_wrong_issuer_rejected(oauth_service, make_id_token):
    """ATTACK 5: ID token with spoofed issuer must be rejected."""
    token = make_id_token(iss="https://fake-google-auth.attacker.org")
    with pytest.raises(OAuthVerificationException, match="issuer is invalid"):
        await oauth_service.verify_id_token(token)


@pytest.mark.asyncio
async def test_13_attack_6_expired_id_token_rejected(oauth_service, make_id_token):
    """ATTACK 6: ID token that has expired must be rejected."""
    token = make_id_token(exp_offset=-100)  # expired in past
    with pytest.raises(OAuthVerificationException, match="expired"):
        await oauth_service.verify_id_token(token)


@pytest.mark.asyncio
async def test_14_attack_7_unverified_email_rejected(oauth_service, make_id_token):
    """ATTACK 7: Google account where email is unverified must be rejected."""
    token = make_id_token(email_verified=False)
    with pytest.raises(OAuthVerificationException, match="email is not verified"):
        await oauth_service.verify_id_token(token)


@pytest.mark.asyncio
async def test_15_nonce_mismatch_rejected(oauth_service, make_id_token):
    """Verify ID token nonce mismatch is strictly rejected."""
    token = make_id_token(nonce="legitimate-nonce-abc")
    with pytest.raises(OAuthVerificationException, match="nonce does not match"):
        await oauth_service.verify_id_token(token, expected_nonce="different-nonce-xyz")


# ==============================================================================
# 5. User Provisioning & Identity Linking Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_16_new_user_provisioning(oauth_service, db_session: AsyncSession):
    """Verify logging in with a new Google identity provisions organization, workspace, and API key."""
    sub = f"google-sub-{uuid.uuid4().hex[:8]}"
    email = f"newuser_{uuid.uuid4().hex[:6]}@example.com"
    claims = {
        "sub": sub,
        "email": email,
        "email_verified": True,
        "name": "Alex Mercer",
        "picture": "https://example.com/alex.jpg",
    }

    session = await oauth_service.authenticate_google_user(db_session, claims)
    assert session.api_key.startswith("ef_ent_")
    assert session.email == email
    assert session.organization_id is not None
    assert session.workspace_id is not None

    # Check identity in database
    stmt = select(OAuthIdentity).where(
        OAuthIdentity.provider == "google", OAuthIdentity.provider_user_id == sub
    )
    res = await db_session.execute(stmt)
    identity = res.scalar_one_or_none()
    assert identity is not None
    assert identity.email == email
    assert identity.user_id == uuid.UUID(session.user_id)


@pytest.mark.asyncio
async def test_17_existing_user_reauthentication(
    oauth_service, db_session: AsyncSession
):
    """Verify existing linked identity logs in without creating duplicate users or orgs."""
    sub = f"google-sub-{uuid.uuid4().hex[:8]}"
    email = f"returning_{uuid.uuid4().hex[:6]}@example.com"
    claims = {
        "sub": sub,
        "email": email,
        "email_verified": True,
        "name": "Returning User",
    }

    # Initial login
    session1 = await oauth_service.authenticate_google_user(db_session, claims)
    # Second login
    session2 = await oauth_service.authenticate_google_user(db_session, claims)

    assert session1.user_id == session2.user_id
    assert session1.organization_id == session2.organization_id

    # Ensure only 1 OAuthIdentity record exists
    stmt = select(OAuthIdentity).where(OAuthIdentity.provider_user_id == sub)
    res = await db_session.execute(stmt)
    identities = res.scalars().all()
    assert len(identities) == 1


@pytest.mark.asyncio
async def test_18_attack_9_identity_takeover_rejected(
    oauth_service, db_session: AsyncSession
):
    """ATTACK 9: Attempting to link an already registered email to a DIFFERENT Google sub must be rejected."""
    email = f"protected_{uuid.uuid4().hex[:6]}@example.com"
    sub_legitimate = "google-sub-legit-123"
    sub_attacker = "google-sub-attacker-456"

    # Legitimate user registers first
    claims_legit = {
        "sub": sub_legitimate,
        "email": email,
        "email_verified": True,
        "name": "Legit User",
    }
    await oauth_service.authenticate_google_user(db_session, claims_legit)

    # Attacker tries to log in with same email under their own Google sub
    claims_attacker = {
        "sub": sub_attacker,
        "email": email,
        "email_verified": True,
        "name": "Attacker",
    }
    with pytest.raises(
        OAuthConflictException, match="already registered to a different Google account"
    ):
        await oauth_service.authenticate_google_user(db_session, claims_attacker)


@pytest.mark.asyncio
async def test_19_attack_10_database_unique_constraint(db_session: AsyncSession):
    """ATTACK 10: Database unique constraint enforces single record per (provider, provider_user_id)."""
    sub = f"sub-dup-{uuid.uuid4().hex[:8]}"
    u1 = uuid.uuid4()
    u2 = uuid.uuid4()

    id1 = OAuthIdentity(
        id=uuid.uuid4(),
        user_id=u1,
        provider="google",
        provider_user_id=sub,
        email="dup1@example.com",
        email_verified=True,
    )
    db_session.add(id1)
    await db_session.commit()

    id2 = OAuthIdentity(
        id=uuid.uuid4(),
        user_id=u2,
        provider="google",
        provider_user_id=sub,
        email="dup2@example.com",
        email_verified=True,
    )
    db_session.add(id2)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


# ==============================================================================
# 6. Tenant Isolation & Access Enforcement Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_20_attack_11_tenant_isolation(oauth_service, db_session: AsyncSession):
    """ATTACK 11: Authenticated Google identity cannot access a different tenant organization."""
    # User 1
    session1 = await oauth_service.authenticate_google_user(
        db_session,
        {
            "sub": f"sub-{uuid.uuid4().hex[:6]}",
            "email": "user1@org1.com",
            "email_verified": True,
        },
    )
    # User 2
    session2 = await oauth_service.authenticate_google_user(
        db_session,
        {
            "sub": f"sub-{uuid.uuid4().hex[:6]}",
            "email": "user2@org2.com",
            "email_verified": True,
        },
    )

    org1_id = uuid.UUID(session1.organization_id)
    org2_id = uuid.UUID(session2.organization_id)
    assert org1_id != org2_id

    # Verify User 1 is not a member of Org 2
    stmt = select(Membership).where(
        Membership.user_id == uuid.UUID(session1.user_id),
        Membership.organization_id == org2_id,
    )
    res = await db_session.execute(stmt)
    assert res.scalar_one_or_none() is None


# ==============================================================================
# 7. Endpoint Integration & Security Leakage Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_21_endpoint_auth_status():
    """Verify /api/v1/auth/status endpoint returns available authentication methods."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/auth/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "google_oauth_enabled" in data["data"]


@pytest.mark.asyncio
async def test_22_endpoint_start_flow_redirect():
    """Verify /api/v1/auth/google/start initiates 307 redirect to Google accounts."""
    transport = ASGITransport(app=app)
    with (
        patch.object(settings, "GOOGLE_CLIENT_ID", TEST_CLIENT_ID),
        patch.object(settings, "GOOGLE_CLIENT_SECRET", SecretStr(TEST_CLIENT_SECRET)),
        patch.object(settings, "GOOGLE_REDIRECT_URI", TEST_REDIRECT_URI),
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/v1/auth/google/start", follow_redirects=False)
            assert resp.status_code == 307
            loc = resp.headers["location"]
            assert "accounts.google.com" in loc
            assert TEST_CLIENT_ID in loc


@pytest.mark.asyncio
async def test_23_endpoint_start_flow_json_format():
    """Verify /api/v1/auth/google/start?format=json returns authorization details as JSON."""
    transport = ASGITransport(app=app)
    with (
        patch.object(settings, "GOOGLE_CLIENT_ID", TEST_CLIENT_ID),
        patch.object(settings, "GOOGLE_CLIENT_SECRET", SecretStr(TEST_CLIENT_SECRET)),
        patch.object(settings, "GOOGLE_REDIRECT_URI", TEST_REDIRECT_URI),
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.get("/api/v1/auth/google/start?format=json")
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert "auth_url" in body["data"]
            assert "state" in body["data"]


@pytest.mark.asyncio
async def test_24_attack_12_secret_leakage_audit():
    """ATTACK 12: Ensure GOOGLE_CLIENT_SECRET is never disclosed in responses or headers."""
    transport = ASGITransport(app=app)
    with (
        patch.object(settings, "GOOGLE_CLIENT_ID", TEST_CLIENT_ID),
        patch.object(settings, "GOOGLE_CLIENT_SECRET", SecretStr(TEST_CLIENT_SECRET)),
        patch.object(settings, "GOOGLE_REDIRECT_URI", TEST_REDIRECT_URI),
    ):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # 1. Inspect /status
            r1 = await ac.get("/api/v1/auth/status")
            assert TEST_CLIENT_SECRET not in r1.text

            # 2. Inspect /google/start
            r2 = await ac.get("/api/v1/auth/google/start?format=json")
            assert TEST_CLIENT_SECRET not in r2.text

            # 3. Inspect simulated error callback
            r3 = await ac.get("/api/v1/auth/google/callback?code=bad&state=bad")
            assert TEST_CLIENT_SECRET not in r3.text


@pytest.mark.asyncio
async def test_25_full_oauth_callback_flow(
    oauth_service, make_id_token, db_session: AsyncSession
):
    """Verify end-to-end OAuth callback exchange, token verification, and session key issuance."""
    flow = await oauth_service.generate_auth_flow(return_to="/overview")
    state = flow["state"]
    nonce = flow["nonce"]
    test_id_token = make_id_token(
        nonce=nonce, sub="full-flow-sub-777", email="fullflow@example.com"
    )

    # Mock exchange_code_for_tokens to return our signed test token
    with patch.object(
        oauth_service,
        "exchange_code_for_tokens",
        AsyncMock(
            return_value={
                "id_token": test_id_token,
                "access_token": "mock-access-token",
            }
        ),
    ):
        # Validate state
        state_data = await oauth_service.validate_state(state)
        # Exchange tokens
        tokens = await oauth_service.exchange_code_for_tokens("test-auth-code")
        # Verify ID token
        claims = await oauth_service.verify_id_token(
            tokens["id_token"], expected_nonce=state_data.get("nonce")
        )
        # Authenticate user
        session = await oauth_service.authenticate_google_user(db_session, claims)

        assert session.api_key.startswith("ef_ent_")
        assert session.email == "fullflow@example.com"
        assert session.return_to == "/overview"
