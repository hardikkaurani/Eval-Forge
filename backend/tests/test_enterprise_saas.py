import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.enterprise.exceptions import PlanQuotaExceededException, TenantAccessViolationException
from app.enterprise.services.rbac_service import RBACService
from app.enterprise.services.quota_service import QuotaService


def test_enterprise_onboarding_and_workspace_lifecycle(client):
    # 1. Seed plans first
    seed_res = client.post("/api/v1/admin/seed-plans")
    assert seed_res.status_code == 200
    assert seed_res.json()["success"] is True

    # 2. Create organization
    user_id = str(uuid.uuid4())
    org_payload = {
        "name": "Acme Corp",
        "logo_url": "https://acme.com/logo.png",
        "custom_domain": f"acme-{uuid.uuid4().hex[:6]}.com",
        "branding_settings": {"primary_color": "#FF0000"},
        "security_policies": {"enforce_mfa": True}
    }
    
    org_res = client.post(f"/api/v1/organizations?user_id={user_id}", json=org_payload)
    assert org_res.status_code == 201
    org_data = org_res.json()["data"]
    org_id = org_data["id"]
    assert org_data["name"] == "Acme Corp"
    assert org_data["custom_domain"] is not None

    # 3. Retrieve organization
    get_res = client.get(f"/api/v1/organizations/{org_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["name"] == "Acme Corp"

    # 4. Update branding and domain
    branding_res = client.post(f"/api/v1/organizations/{org_id}/branding", json={"primary_color": "#00FF00"})
    assert branding_res.status_code == 200
    assert branding_res.json()["data"]["branding_settings"]["primary_color"] == "#00FF00"

    domain_res = client.post(f"/api/v1/organizations/{org_id}/domain?domain=custom.acme.com")
    assert domain_res.status_code == 200
    assert domain_res.json()["data"]["custom_domain"] == "custom.acme.com"

    # 5. Invite a member
    invite_payload = {
        "email": "dev@acme.com",
        "role": "Developer"
    }
    invite_res = client.post(f"/api/v1/organizations/{org_id}/invitations?invited_by={user_id}", json=invite_payload)
    assert invite_res.status_code == 201
    assert invite_res.json()["data"]["email"] == "dev@acme.com"

    # 6. Create workspace
    ws_payload = {
        "organization_id": org_id,
        "name": "Staging Environment",
        "description": "Acme Staging workspace"
    }
    ws_res = client.post("/api/v1/workspaces", json=ws_payload)
    assert ws_res.status_code == 201
    ws_data = ws_res.json()["data"]
    ws_id = ws_data["id"]
    assert ws_data["name"] == "Staging Environment"

    # 7. List workspaces
    list_ws_res = client.get(f"/api/v1/workspaces?org_id={org_id}")
    assert list_ws_res.status_code == 200
    assert len(list_ws_res.json()["data"]) == 1


def test_enterprise_billing_and_subscriptions(client):
    # Seed plans first
    seed_res = client.post("/api/v1/admin/seed-plans")
    assert seed_res.status_code == 200

    # Setup organization
    user_id = str(uuid.uuid4())
    org_res = client.post(
        f"/api/v1/organizations?user_id={user_id}",
        json={"name": "Billing Org", "custom_domain": f"bill-{uuid.uuid4().hex[:6]}.com"}
    )
    org_id = org_res.json()["data"]["id"]

    # 1. Create checkout session URL
    checkout_res = client.post(f"/api/v1/billing/checkout?org_id={org_id}&plan_name=Pro&provider=stripe")
    assert checkout_res.status_code == 200
    assert "checkout.stripe.com" in checkout_res.json()["data"]

    # 2. Activate subscription
    sub_res = client.post(f"/api/v1/billing/subscriptions?org_id={org_id}&plan_name=Pro")
    assert sub_res.status_code == 200
    assert sub_res.json()["data"]["status"] == "active"

    # 3. List invoice history
    invoice_res = client.get(f"/api/v1/billing/invoices?org_id={org_id}")
    assert invoice_res.status_code == 200
    assert len(invoice_res.json()["data"]) > 0


def test_enterprise_api_keys_and_audit(client):
    # Setup org and workspace
    user_id = str(uuid.uuid4())
    org_res = client.post(
        f"/api/v1/organizations?user_id={user_id}",
        json={"name": "API Key Org", "custom_domain": f"key-{uuid.uuid4().hex[:6]}.com"}
    )
    org_id = org_res.json()["data"]["id"]

    ws_res = client.post(
        "/api/v1/workspaces",
        json={"organization_id": org_id, "name": "Key Workspace"}
    )
    ws_id = ws_res.json()["data"]["id"]

    # 1. Generate API Key
    key_payload = {
        "organization_id": org_id,
        "workspace_id": ws_id,
        "name": "Prod API Key",
        "scopes": ["read:all", "write:evaluations"],
        "expires_in_days": 15
    }
    key_res = client.post("/api/v1/api-keys", json=key_payload)
    assert key_res.status_code == 201
    key_data = key_res.json()["data"]
    assert "api_key" in key_data
    assert key_data["api_key"].startswith("ef_ent_")
    key_id = key_data["details"]["id"]

    # 2. Revoke API Key
    revoke_res = client.delete(f"/api/v1/api-keys/{key_id}")
    assert revoke_res.status_code == 200
    assert revoke_res.json()["data"] is True


@pytest.mark.asyncio
async def test_rbac_and_quota_exceptions(db_session: AsyncSession):
    rbac = RBACService()
    quota = QuotaService()

    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # 1. Verify custom role creation
    role = await rbac.create_custom_role(db_session, org_id, "Tester", ["test:run"])
    assert role.name == "Tester"
    assert "test:run" in role.permissions

    # 2. Trigger quota exceed exception manually
    with pytest.raises(PlanQuotaExceededException):
        await quota.record_usage(
            db=db_session,
            org_id=org_id,
            workspace_id=uuid.uuid4(),
            metric="api_requests",
            value=6000000.0  # Way above any standard default quota limit
        )


def test_admin_console_endpoints(client):
    # Verify we can list all organizations in the system
    orgs_res = client.get("/api/v1/admin/organizations")
    assert orgs_res.status_code == 200
    assert isinstance(orgs_res.json()["data"], list)

    # Verify SSO identity provider settings registration
    sso_res = client.post(
        f"/api/v1/admin/sso/identity-providers?org_id={uuid.uuid4()}&provider_type=oidc"
        "&metadata_url=https://auth.acme.com/.well-known/openid-configuration"
        "&client_id=client_123&client_secret=secret_xyz"
    )
    assert sso_res.status_code == 200
    assert sso_res.json()["data"]["provider"] == "oidc"
