import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.enterprise.exceptions import (
    BillingGatewayException,
    PlanQuotaExceededException,
    TenantAccessViolationException,
)
from app.enterprise.models import Invitation, Membership, Quota, Subscription
from app.enterprise.services.billing_service import BillingService
from app.enterprise.services.organization_service import OrganizationService
from app.enterprise.services.quota_service import QuotaService


@pytest.mark.asyncio
async def test_organization_creation_assigns_owner(db_session: AsyncSession):
    org_service = OrganizationService()
    user_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session,
        name="Acme Enterprise",
        user_id=user_id,
        custom_domain="acme.evalforge.io",
    )

    assert org is not None
    assert org.name == "Acme Enterprise"
    assert org.custom_domain == "acme.evalforge.io"

    # Verify membership created with Owner role
    stmt = select(Membership).where(
        Membership.organization_id == org.id, Membership.user_id == user_id
    )
    res = await db_session.execute(stmt)
    membership = res.scalar_one_or_none()
    assert membership is not None
    assert membership.is_active is True


@pytest.mark.asyncio
async def test_member_invitation_hashing_and_acceptance(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Beta Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # 1. Invite a new member
    invite_res = await org_service.invite_member(
        db_session,
        org_id=org_uuid,
        email="dev@betacorp.com",
        role_name="Member",
        invited_by=owner_id,
    )
    raw_token = invite_res["raw_token"]
    assert raw_token is not None
    assert invite_res["status"] == "pending"

    # Verify raw token is NOT stored plain text in database
    stmt = select(Invitation).where(Invitation.organization_id == org_uuid)
    res = await db_session.execute(stmt)
    inv_db = res.scalar_one_or_none()
    assert inv_db is not None
    assert str(inv_db.token) != raw_token
    assert len(str(inv_db.token)) == 64  # SHA-256 hex string

    # 2. Accept invitation
    new_user_id = uuid.uuid4()
    membership = await org_service.accept_invitation(db_session, raw_token, new_user_id)
    assert membership.organization_id == org_uuid
    assert membership.user_id == new_user_id
    assert membership.is_active is True

    # 3. Verify token cannot be re-used
    with pytest.raises(TenantAccessViolationException, match="already accepted"):
        await org_service.accept_invitation(db_session, raw_token, uuid.uuid4())


@pytest.mark.asyncio
async def test_sole_owner_removal_prevented(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Security Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    members = await org_service.list_members(db_session, org_uuid)
    assert len(members) == 1
    sole_owner_membership_id = uuid.UUID(members[0]["id"])

    # Attempt to remove the only owner
    with pytest.raises(
        TenantAccessViolationException, match="Cannot remove the sole Owner"
    ):
        await org_service.remove_member(db_session, org_uuid, sole_owner_membership_id)


@pytest.mark.asyncio
async def test_concurrency_safe_quota_metering(db_session: AsyncSession):
    quota_service = QuotaService()
    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Record usage 5 times (simulating atomic increments)
    for _i in range(5):
        record = await quota_service.record_usage(
            db_session,
            org_id=org_id,
            workspace_id=ws_id,
            metric="evaluations",
            value=10.0,
        )
        assert record.value == 10.0

    status = await quota_service.check_quota_status(
        db_session, org_id=org_id, workspace_id=ws_id, metric="evaluations"
    )
    assert status["current"] == 50.0
    assert status["status"] == "ok"

    # Exceed quota
    quota_stmt = select(Quota).where(
        Quota.organization_id == org_id, Quota.workspace_id == ws_id
    )
    quota_obj = (await db_session.execute(quota_stmt)).scalar_one()
    quota_obj.limit_value = 60.0
    await db_session.commit()

    with pytest.raises(PlanQuotaExceededException, match="Hard quota limit"):
        await quota_service.record_usage(
            db_session,
            org_id=org_id,
            workspace_id=ws_id,
            metric="evaluations",
            value=20.0,
        )


@pytest.mark.asyncio
async def test_stripe_checkout_server_side_price_mapping(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Stripe Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Valid plan generates checkout URL
    url = await billing_service.create_checkout_session(db_session, org_uuid, "Pro")
    assert "stripe.com" in url or "checkout" in url

    # Invalid plan is rejected server-side
    with pytest.raises(Exception, match="Invalid plan name"):
        await billing_service.create_checkout_session(
            db_session, org_uuid, "FreeEnterpriseSuperHacked"
        )


@pytest.mark.asyncio
async def test_stripe_webhook_idempotency_and_state_machine(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Webhook Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    event_id = f"evt_test_{uuid.uuid4().hex[:12]}"
    event_payload: dict[str, Any] = {
        "id": event_id,
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": f"cus_{uuid.uuid4().hex[:8]}",
                "subscription": f"sub_{uuid.uuid4().hex[:8]}",
                "metadata": {
                    "organization_id": str(org.id),
                    "plan_name": "Pro",
                },
            }
        },
    }
    payload_bytes = json.dumps(event_payload).encode("utf-8")

    # 1. Process first delivery
    res1 = await billing_service.process_stripe_webhook(
        db_session, payload_bytes, sig_header=None
    )
    assert res1["status"] == "processed"

    # Verify subscription activated in database
    sub = await billing_service.get_active_subscription(db_session, org_uuid)
    assert sub is not None
    assert sub.status == "active"

    # 2. Process duplicate event (replayed delivery)
    res2 = await billing_service.process_stripe_webhook(
        db_session, payload_bytes, sig_header=None
    )
    assert res2["status"] == "idempotent_duplicate"

    # Verify duplicate event did not create duplicate subscriptions
    stmt = select(Subscription).where(Subscription.organization_id == org_uuid)
    all_subs = (await db_session.execute(stmt)).scalars().all()
    assert len(all_subs) == 1


@pytest.mark.asyncio
async def test_subscription_lifecycle_cancellation_and_past_due(
    db_session: AsyncSession,
):
    billing_service = BillingService()
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Lifecycle Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    stripe_sub_id = f"sub_{uuid.uuid4().hex[:8]}"
    cus_id = f"cus_{uuid.uuid4().hex[:8]}"
    org.stripe_customer_id = cus_id
    await db_session.commit()

    # Activate
    await billing_service.create_subscription(
        db_session, org_uuid, "Team", stripe_subscription_id=stripe_sub_id
    )

    # 1. Simulate invoice payment failed event
    failed_payload: dict[str, Any] = {
        "id": f"evt_fail_{uuid.uuid4().hex[:8]}",
        "type": "invoice.payment_failed",
        "data": {"object": {"customer": cus_id}},
    }
    await billing_service.process_stripe_webhook(
        db_session, json.dumps(failed_payload).encode("utf-8"), sig_header=None
    )

    stmt = select(Subscription).where(
        Subscription.stripe_subscription_id == stripe_sub_id
    )
    sub_obj = (await db_session.execute(stmt)).scalar_one_or_none()
    assert sub_obj is not None
    assert sub_obj.status == "past_due"

    # 2. Simulate subscription deleted event
    deleted_payload: dict[str, Any] = {
        "id": f"evt_del_{uuid.uuid4().hex[:8]}",
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": stripe_sub_id, "status": "canceled"}},
    }
    await billing_service.process_stripe_webhook(
        db_session, json.dumps(deleted_payload).encode("utf-8"), sig_header=None
    )

    sub_obj2 = (await db_session.execute(stmt)).scalar_one_or_none()
    assert sub_obj2 is not None
    assert sub_obj2.status == "canceled"


def test_api_stripe_public_webhook_listener(client: TestClient):
    evt_id = f"evt_pub_{uuid.uuid4().hex[:12]}"
    payload: dict[str, Any] = {
        "id": evt_id,
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "customer": "cus_pub_test_123",
                "amount_paid": 4900,
                "hosted_invoice_url": "https://invoice.stripe.com/pub_123",
            }
        },
    }
    res = client.post(
        "/api/v1/billing/webhooks/stripe",
        content=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "processed"
    assert data["event_id"] == evt_id

    # Duplicate delivery is idempotent
    res_dup = client.post(
        "/api/v1/billing/webhooks/stripe",
        content=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )
    assert res_dup.status_code == 200
    assert res_dup.json()["status"] == "idempotent_duplicate"


@pytest.mark.asyncio
async def test_member_role_update_and_sole_owner_demotion_prevention(
    db_session: AsyncSession,
):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Role Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    members = await org_service.list_members(db_session, org_uuid)
    assert len(members) == 1
    owner_membership_id = uuid.UUID(members[0]["id"])

    # 1. Sole owner cannot be demoted to Member
    with pytest.raises(
        TenantAccessViolationException, match="Cannot demote the sole Owner"
    ):
        await org_service.update_member_role(
            db_session, org_uuid, owner_membership_id, "Member"
        )

    # 2. Add second user as Member
    user2_id = uuid.uuid4()
    invite = await org_service.invite_member(
        db_session, org_uuid, "u2@role.com", "Member", owner_id
    )
    m2 = await org_service.accept_invitation(db_session, invite["raw_token"], user2_id)
    m2_uuid = uuid.UUID(str(m2.id))

    # 3. Promote second user to Owner
    m2_updated = await org_service.update_member_role(
        db_session, org_uuid, m2_uuid, "Owner"
    )
    assert m2_updated.role is not None
    assert m2_updated.role.name == "Owner"

    # 4. Now original owner CAN be demoted because another Owner exists
    m1_demoted = await org_service.update_member_role(
        db_session, org_uuid, owner_membership_id, "Admin"
    )
    assert m1_demoted.role is not None
    assert m1_demoted.role.name == "Admin"


@pytest.mark.asyncio
async def test_atomic_ownership_transfer_lifecycle(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    target_id = uuid.uuid4()

    org = await org_service.create_organization(
        db_session, name="Transfer Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Add target as member
    invite = await org_service.invite_member(
        db_session, org_uuid, "target@transfer.com", "Member", owner_id
    )
    await org_service.accept_invitation(db_session, invite["raw_token"], target_id)

    # Transfer ownership
    success = await org_service.transfer_ownership(
        db_session,
        org_id=org_uuid,
        current_owner_user_id=owner_id,
        target_user_id=target_id,
        demoted_role_name="Admin",
    )
    assert success is True

    # Verify target is now Owner and original owner is Admin
    members = await org_service.list_members(db_session, org_uuid)
    roles_by_user = {m["user_id"]: m["role"] for m in members}
    assert roles_by_user[str(target_id)] == "Owner"
    assert roles_by_user[str(owner_id)] == "Admin"


@pytest.mark.asyncio
async def test_ownership_transfer_rejects_non_member(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    outside_user_id = uuid.uuid4()

    org = await org_service.create_organization(
        db_session, name="Secure Vault", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    with pytest.raises(
        TenantAccessViolationException, match="Target user is not an active member"
    ):
        await org_service.transfer_ownership(
            db_session,
            org_id=org_uuid,
            current_owner_user_id=owner_id,
            target_user_id=outside_user_id,
        )


@pytest.mark.asyncio
async def test_cross_org_membership_isolation(db_session: AsyncSession):
    org_service = OrganizationService()
    owner1_id = uuid.uuid4()
    owner2_id = uuid.uuid4()

    org1 = await org_service.create_organization(
        db_session, name="Tenant Alpha", user_id=owner1_id
    )
    org2 = await org_service.create_organization(
        db_session, name="Tenant Beta", user_id=owner2_id
    )
    org1_uuid = uuid.UUID(str(org1.id))
    org2_uuid = uuid.UUID(str(org2.id))

    members_org1 = await org_service.list_members(db_session, org1_uuid)
    m1_id = uuid.UUID(members_org1[0]["id"])

    # Attempt to delete Tenant Alpha's member using Tenant Beta's org context
    with pytest.raises(
        TenantAccessViolationException, match="Member not found in organization"
    ):
        await org_service.remove_member(db_session, org2_uuid, m1_id)

    # Attempt to update Tenant Alpha's member role using Tenant Beta's org context
    with pytest.raises(
        TenantAccessViolationException, match="Member not found in organization"
    ):
        await org_service.update_member_role(db_session, org2_uuid, m1_id, "Admin")


@pytest.mark.asyncio
async def test_organization_creation_rollback_on_membership_failure(
    db_session: AsyncSession,
):
    org_service = OrganizationService()
    user_id = uuid.uuid4()
    org_name = f"FailedOrg_{uuid.uuid4().hex[:8]}"

    # Simulate error during creator membership creation
    from unittest.mock import patch

    with patch.object(
        org_service,
        "_get_or_create_default_role",
        side_effect=RuntimeError("Simulated DB error during owner role assignment"),
    ):
        with pytest.raises(RuntimeError, match="Simulated DB error"):
            await org_service.create_organization(
                db_session, name=org_name, user_id=user_id
            )

    # Verify organization creation was completely rolled back
    from app.enterprise.models import Organization

    stmt = select(Organization).where(Organization.name == org_name)
    res = await db_session.execute(stmt)
    org_in_db = res.scalar_one_or_none()
    assert org_in_db is None, "Orphan organization must not exist in DB after failure"


@pytest.mark.asyncio
async def test_database_enforces_membership_uniqueness(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="UniqueOrg", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Attempt to directly insert duplicate membership for owner in same org
    from sqlalchemy.exc import IntegrityError

    duplicate_membership = Membership(
        id=uuid.uuid4(),
        organization_id=org_uuid,
        user_id=owner_id,
        is_active=True,
    )
    db_session.add(duplicate_membership)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_rbac_role_permission_hierarchy_and_fail_closed(db_session: AsyncSession):
    from app.enterprise.services.rbac_service import RBACService

    rbac_service = RBACService()
    org_service = OrganizationService()

    # 1. Setup Organization with Owner
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="RBAC Enterprise", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # 2. Add Admin, Member, and Viewer
    admin_id = uuid.uuid4()
    member_id = uuid.uuid4()
    viewer_id = uuid.uuid4()

    inv_admin = await org_service.invite_member(
        db_session, org_uuid, "admin@rbac.com", "Admin", owner_id
    )
    await org_service.accept_invitation(db_session, inv_admin["raw_token"], admin_id)

    inv_member = await org_service.invite_member(
        db_session, org_uuid, "member@rbac.com", "Member", owner_id
    )
    await org_service.accept_invitation(db_session, inv_member["raw_token"], member_id)

    inv_viewer = await org_service.invite_member(
        db_session, org_uuid, "viewer@rbac.com", "Viewer", owner_id
    )
    await org_service.accept_invitation(db_session, inv_viewer["raw_token"], viewer_id)

    # 3. Verify Owner permissions (Full Authority)
    assert (
        await rbac_service.has_permission(db_session, org_uuid, owner_id, "org:delete")
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, owner_id, "ownership:transfer"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, owner_id, "billing:manage"
        )
        is True
    )

    # 4. Verify Admin permissions (Cannot transfer ownership or delete org)
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, admin_id, "members:invite"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, admin_id, "billing:manage"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, admin_id, "ownership:transfer"
        )
        is False
    )
    assert (
        await rbac_service.has_permission(db_session, org_uuid, admin_id, "org:delete")
        is False
    )

    # 5. Verify Member permissions (Operational only; no billing/admin/delete)
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, member_id, "projects:write"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, member_id, "datasets:write"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, member_id, "evaluations:create"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, member_id, "members:invite"
        )
        is False
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, member_id, "billing:manage"
        )
        is False
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, member_id, "projects:delete"
        )
        is False
    )

    # 6. Verify Viewer permissions (Read-only on datasets/projects/evaluations/audit)
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, viewer_id, "datasets:read"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, viewer_id, "evaluations:read"
        )
        is True
    )
    assert (
        await rbac_service.has_permission(db_session, org_uuid, viewer_id, "audit:read")
        is True
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, viewer_id, "datasets:write"
        )
        is False
    )
    assert (
        await rbac_service.has_permission(
            db_session, org_uuid, viewer_id, "evaluations:create"
        )
        is False
    )


@pytest.mark.asyncio
async def test_rbac_privilege_escalation_prevention(db_session: AsyncSession):
    from app.enterprise.services.rbac_service import RBACService

    rbac_service = RBACService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    member_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Escalation Guard Corp", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    inv = await org_service.invite_member(
        db_session, org_uuid, "victim@guard.com", "Member", owner_id
    )
    await org_service.accept_invitation(db_session, inv["raw_token"], member_id)

    # 1. Member cannot require administrative privileges (fail closed)
    with pytest.raises(
        TenantAccessViolationException,
        match="Missing required permission 'members:update'",
    ):
        await rbac_service.require_permission(
            db_session, org_uuid, member_id, "members:update"
        )

    with pytest.raises(
        TenantAccessViolationException,
        match="Missing required permission 'ownership:transfer'",
    ):
        await rbac_service.require_permission(
            db_session, org_uuid, member_id, "ownership:transfer"
        )


@pytest.mark.asyncio
async def test_rbac_cross_org_isolation_and_inactive_membership(
    db_session: AsyncSession,
):
    from app.enterprise.services.rbac_service import RBACService

    rbac_service = RBACService()
    org_service = OrganizationService()

    owner1_id = uuid.uuid4()
    owner2_id = uuid.uuid4()
    org1 = await org_service.create_organization(
        db_session, name="Org Alpha", user_id=owner1_id
    )
    org2 = await org_service.create_organization(
        db_session, name="Org Beta", user_id=owner2_id
    )
    org1_uuid = uuid.UUID(str(org1.id))
    org2_uuid = uuid.UUID(str(org2.id))

    # Owner of Org 1 has NO permissions in Org 2
    assert (
        await rbac_service.has_permission(db_session, org2_uuid, owner1_id, "org:read")
        is False
    )
    with pytest.raises(
        TenantAccessViolationException, match="Missing required permission"
    ):
        await rbac_service.require_permission(
            db_session, org2_uuid, owner1_id, "org:read"
        )

    # Inactive membership in Org 1 yields no permissions
    stmt = select(Membership).where(
        Membership.organization_id == org1_uuid, Membership.user_id == owner1_id
    )
    membership = (await db_session.execute(stmt)).scalar_one()
    membership.is_active = False
    await db_session.commit()

    assert (
        await rbac_service.has_permission(db_session, org1_uuid, owner1_id, "org:read")
        is False
    )
    assert (
        await rbac_service.has_permission(
            db_session, org1_uuid, owner1_id, "ownership:transfer"
        )
        is False
    )


@pytest.mark.asyncio
async def test_invitation_revocation_lifecycle(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Revoke Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Create invitation
    invite = await org_service.invite_member(
        db_session, org_uuid, "victim@revoke.com", "Member", owner_id
    )
    inv_id = uuid.UUID(invite["id"])
    raw_token = invite["raw_token"]

    # Revoke invitation
    revoked = await org_service.revoke_invitation(db_session, org_uuid, inv_id)
    assert revoked is True

    # Acceptance of revoked invitation must fail closed
    with pytest.raises(TenantAccessViolationException, match="already revoked"):
        await org_service.accept_invitation(db_session, raw_token, uuid.uuid4())

    # Cannot revoke already revoked invitation
    with pytest.raises(TenantAccessViolationException, match="already revoked"):
        await org_service.revoke_invitation(db_session, org_uuid, inv_id)


@pytest.mark.asyncio
async def test_invitation_resend_and_rotation(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Resend Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    invite1 = await org_service.invite_member(
        db_session, org_uuid, "rotate@resend.com", "Member", owner_id
    )
    inv_id = uuid.UUID(invite1["id"])
    old_raw_token = invite1["raw_token"]

    # Resend rotates token
    invite2 = await org_service.resend_invitation(db_session, org_uuid, inv_id)
    new_raw_token = invite2["raw_token"]
    assert new_raw_token != old_raw_token

    # Old token fails
    with pytest.raises(
        TenantAccessViolationException, match="Invalid invitation token"
    ):
        await org_service.accept_invitation(db_session, old_raw_token, uuid.uuid4())

    # New token succeeds
    user2_id = uuid.uuid4()
    membership = await org_service.accept_invitation(
        db_session, new_raw_token, user2_id
    )
    assert membership.user_id == user2_id
    assert membership.organization_id == org_uuid


@pytest.mark.asyncio
async def test_invitation_expiration_enforcement(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Expire Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    invite = await org_service.invite_member(
        db_session, org_uuid, "late@expire.com", "Member", owner_id
    )
    inv_id = uuid.UUID(invite["id"])
    raw_token = invite["raw_token"]

    # Force expiration in database
    stmt = select(Invitation).where(Invitation.id == inv_id)
    inv_db = (await db_session.execute(stmt)).scalar_one()
    inv_db.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    await db_session.commit()

    # Expired token rejection
    with pytest.raises(TenantAccessViolationException, match="has expired"):
        await org_service.accept_invitation(db_session, raw_token, uuid.uuid4())


@pytest.mark.asyncio
async def test_invitation_cannot_grant_owner_role(db_session: AsyncSession):
    org_service = OrganizationService()
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Owner Guard Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Direct invite with Owner role must be rejected
    with pytest.raises(
        TenantAccessViolationException,
        match="Cannot invite users directly with Owner role",
    ):
        await org_service.invite_member(
            db_session, org_uuid, "hacker@guard.com", "Owner", owner_id
        )


@pytest.mark.asyncio
async def test_cross_tenant_invitation_isolation(db_session: AsyncSession):
    org_service = OrganizationService()
    owner1_id = uuid.uuid4()
    owner2_id = uuid.uuid4()

    org1 = await org_service.create_organization(
        db_session, name="Tenant 1", user_id=owner1_id
    )
    org2 = await org_service.create_organization(
        db_session, name="Tenant 2", user_id=owner2_id
    )
    org1_uuid = uuid.UUID(str(org1.id))
    org2_uuid = uuid.UUID(str(org2.id))

    invite_t1 = await org_service.invite_member(
        db_session, org1_uuid, "member@tenant1.com", "Member", owner1_id
    )
    inv_id = uuid.UUID(invite_t1["id"])

    # Tenant 2 attempting to revoke Tenant 1's invitation must fail
    with pytest.raises(
        TenantAccessViolationException, match="Invitation not found in organization"
    ):
        await org_service.revoke_invitation(db_session, org2_uuid, inv_id)

    # Tenant 2 attempting to resend Tenant 1's invitation must fail
    with pytest.raises(
        TenantAccessViolationException, match="Invitation not found in organization"
    ):
        await org_service.resend_invitation(db_session, org2_uuid, inv_id)


# ============================================================================
# MILESTONE 5: Plans & Entitlements Tests
# ============================================================================


@pytest.mark.asyncio
async def test_plan_and_entitlements_resolution(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Entitlement Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # 1. Unsubscribed org defaults to Starter entitlements
    starter_ent = await billing_service.get_organization_entitlements(
        db_session, org_uuid
    )
    assert starter_ent["plan_name"] == "Starter"
    assert starter_ent["limits"]["evaluations"] == 100
    assert starter_ent["features"]["rag_evaluation"] is False
    assert (
        await billing_service.has_entitlement(db_session, org_uuid, "rag_evaluation")
        is False
    )

    # Requiring premium entitlement fails closed
    with pytest.raises(TenantAccessViolationException, match="Upgrade required"):
        await billing_service.require_entitlement(
            db_session, org_uuid, "rag_evaluation"
        )

    # 2. Upgrade to Pro plan activates premium features
    await billing_service.create_subscription(db_session, org_uuid, "Pro")
    pro_ent = await billing_service.get_organization_entitlements(db_session, org_uuid)
    assert pro_ent["plan_name"] == "Pro"
    assert pro_ent["limits"]["evaluations"] == 1000
    assert pro_ent["features"]["rag_evaluation"] is True
    assert (
        await billing_service.has_entitlement(db_session, org_uuid, "rag_evaluation")
        is True
    )


@pytest.mark.asyncio
async def test_entitlement_fail_closed_on_expired_subscription(
    db_session: AsyncSession,
):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Expired Sub Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Activate Pro subscription
    sub = await billing_service.create_subscription(db_session, org_uuid, "Pro")
    assert (
        await billing_service.has_entitlement(db_session, org_uuid, "rag_evaluation")
        is True
    )

    # Mark subscription canceled
    sub.status = "canceled"
    await db_session.commit()

    # Entitlement immediately fails closed back to Starter baseline
    ent = await billing_service.get_organization_entitlements(db_session, org_uuid)
    assert ent["plan_name"] == "Starter"
    assert (
        await billing_service.has_entitlement(db_session, org_uuid, "rag_evaluation")
        is False
    )


# ============================================================================
# MILESTONE 6: Usage Metering Tests
# ============================================================================


@pytest.mark.asyncio
async def test_usage_metering_atomic_increment(db_session: AsyncSession):
    quota_service = QuotaService()
    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Record valid usage increments
    rec1 = await quota_service.record_usage(
        db_session, org_id, ws_id, "evaluations", 10.0
    )
    assert rec1.value == 10.0

    rec2 = await quota_service.record_usage(
        db_session, org_id, ws_id, "evaluations", 15.0
    )
    assert rec2.value == 15.0

    # Quota status reflects combined usage
    status = await quota_service.check_quota_status(
        db_session, org_id, ws_id, "evaluations"
    )
    assert status["current"] == 25.0


@pytest.mark.asyncio
async def test_usage_negative_value_rejected(db_session: AsyncSession):
    quota_service = QuotaService()
    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    with pytest.raises(ValueError, match="Usage increment value must be non-negative"):
        await quota_service.record_usage(db_session, org_id, ws_id, "evaluations", -5.0)


# ============================================================================
# MILESTONE 7: Atomic Quotas Tests
# ============================================================================


@pytest.mark.asyncio
async def test_quota_atomic_reservation_and_release(db_session: AsyncSession):
    quota_service = QuotaService()
    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Reserve within limits (default Starter limit = 100)
    res = await quota_service.reserve_quota(
        db_session, org_id, ws_id, "evaluations", 30.0
    )
    assert res is True

    status = await quota_service.check_quota_status(
        db_session, org_id, ws_id, "evaluations"
    )
    assert status["current"] == 30.0

    # Release 10 units
    rel = await quota_service.release_quota(
        db_session, org_id, ws_id, "evaluations", 10.0
    )
    assert rel is True

    status2 = await quota_service.check_quota_status(
        db_session, org_id, ws_id, "evaluations"
    )
    assert status2["current"] == 20.0

    # Attempting to exceed remaining capacity (80 left) fails closed
    with pytest.raises(PlanQuotaExceededException, match="Quota reservation failed"):
        await quota_service.reserve_quota(
            db_session, org_id, ws_id, "evaluations", 85.0
        )


# ============================================================================
# MILESTONES 8, 9, 10: Stripe Customer & Checkout Lifecycle Tests
# ============================================================================


@pytest.mark.asyncio
async def test_stripe_customer_lifecycle_and_reuse(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Stripe Cust Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # 1. First retrieval generates and saves customer ID
    cust1 = await billing_service.get_or_create_stripe_customer(db_session, org_uuid)
    assert cust1.startswith("cus_")

    # 2. Subsequent call reuses existing customer ID without duplicate creation
    cust2 = await billing_service.get_or_create_stripe_customer(db_session, org_uuid)
    assert cust1 == cust2


@pytest.mark.asyncio
async def test_stripe_checkout_session_creation_with_trusted_price(
    db_session: AsyncSession,
):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Checkout Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Valid plan generates checkout URL
    checkout_url = await billing_service.create_checkout_session(
        db_session, org_uuid, "Pro"
    )
    assert "checkout.stripe.com" in checkout_url or "status=success" in checkout_url

    # Invalid/unauthorized plan name is rejected
    with pytest.raises(BillingGatewayException, match="Invalid plan name"):
        await billing_service.create_checkout_session(
            db_session, org_uuid, "UnlimitedHackerPlan"
        )


@pytest.mark.asyncio
async def test_checkout_does_not_activate_subscription_prematurely(
    db_session: AsyncSession,
):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Pending Checkout Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Initiate checkout for Pro plan
    _ = await billing_service.create_checkout_session(db_session, org_uuid, "Pro")

    # Subscription should NOT be activated before webhook confirmation
    active_sub = await billing_service.get_active_subscription(db_session, org_uuid)
    assert active_sub is None


# ============================================================================
# MILESTONE 11: Stripe Customer Portal Tests
# ============================================================================


@pytest.mark.asyncio
async def test_customer_portal_creation_success(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Portal Test Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    portal_url = await billing_service.create_customer_portal_session(
        db_session, org_uuid, return_url="https://evalforge.com/settings/billing"
    )
    assert "billing.stripe.com" in portal_url


@pytest.mark.asyncio
async def test_customer_portal_malicious_return_url_rejected(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Malicious Portal Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Reject javascript: protocol
    with pytest.raises(BillingGatewayException, match="Invalid return URL scheme"):
        await billing_service.create_customer_portal_session(
            db_session, org_uuid, return_url="javascript:alert(1)"
        )

    # Reject data: protocol
    with pytest.raises(BillingGatewayException, match="Invalid return URL scheme"):
        await billing_service.create_customer_portal_session(
            db_session,
            org_uuid,
            return_url="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
        )


@pytest.mark.asyncio
async def test_customer_portal_does_not_mutate_subscription(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Portal State Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    # Unsubscribed org opening portal remains unsubscribed
    _ = await billing_service.create_customer_portal_session(db_session, org_uuid)
    active_sub = await billing_service.get_active_subscription(db_session, org_uuid)
    assert active_sub is None


# ============================================================================
# MILESTONE 12 & 13: Webhooks & State Machine Tests
# ============================================================================


@pytest.mark.asyncio
async def test_webhook_raw_body_malformed_fails_closed(db_session: AsyncSession):
    billing_service = BillingService()

    with pytest.raises(BillingGatewayException, match="Invalid JSON"):
        await billing_service.process_stripe_webhook(
            db_session, b"non-json-corrupted-bytes", None
        )


@pytest.mark.asyncio
async def test_webhook_missing_event_id_fails_closed(db_session: AsyncSession):
    billing_service = BillingService()
    payload = json.dumps({"type": "checkout.session.completed"}).encode("utf-8")

    with pytest.raises(BillingGatewayException, match="Malformed Stripe event"):
        await billing_service.process_stripe_webhook(db_session, payload, None)


@pytest.mark.asyncio
async def test_billing_state_machine_cancel_at_period_end_and_stale_event(
    db_session: AsyncSession,
):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Cancel Period Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))

    stripe_sub_id = f"sub_{uuid.uuid4().hex[:14]}"
    sub = await billing_service.create_subscription(
        db_session, org_uuid, "Pro", stripe_subscription_id=stripe_sub_id
    )
    assert sub.status == "active"
    assert sub.cancel_at_period_end is False

    # 1. Update with cancel_at_period_end = True keeps status active until period end
    update_event = {
        "id": f"evt_upd_{uuid.uuid4().hex[:12]}",
        "type": "customer.subscription.updated",
        "created": int(datetime.now(timezone.utc).timestamp()),
        "data": {
            "object": {
                "id": stripe_sub_id,
                "status": "active",
                "cancel_at_period_end": True,
            }
        },
    }
    await billing_service.process_stripe_webhook(
        db_session, json.dumps(update_event).encode("utf-8"), None
    )

    stmt = select(Subscription).where(Subscription.id == sub.id)
    sub_after = (await db_session.execute(stmt)).scalar_one()
    assert sub_after.status == "active"
    assert sub_after.cancel_at_period_end is True

    # 2. Deletion event cancels subscription
    del_event = {
        "id": f"evt_del_{uuid.uuid4().hex[:12]}",
        "type": "customer.subscription.deleted",
        "created": int(datetime.now(timezone.utc).timestamp() + 10),
        "data": {"object": {"id": stripe_sub_id, "status": "canceled"}},
    }
    await billing_service.process_stripe_webhook(
        db_session, json.dumps(del_event).encode("utf-8"), None
    )

    sub_del = (await db_session.execute(stmt)).scalar_one()
    assert sub_del.status == "canceled"

    # 3. Out of order stale update event arriving after cancellation cannot revive subscription
    stale_event = {
        "id": f"evt_stale_{uuid.uuid4().hex[:12]}",
        "type": "customer.subscription.updated",
        "created": int(datetime.now(timezone.utc).timestamp() - 100),
        "data": {
            "object": {
                "id": stripe_sub_id,
                "status": "active",
                "cancel_at_period_end": False,
            }
        },
    }
    await billing_service.process_stripe_webhook(
        db_session, json.dumps(stale_event).encode("utf-8"), None
    )

    sub_final = (await db_session.execute(stmt)).scalar_one()
    assert sub_final.status == "canceled"


# ============================================================================
# MILESTONE 14: Billing Idempotency Tests
# ============================================================================


@pytest.mark.asyncio
async def test_webhook_100_times_replay_idempotent(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()

    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="Replay Org", user_id=owner_id
    )
    cust_id = f"cus_replay_{uuid.uuid4().hex[:12]}"
    org.stripe_customer_id = cust_id
    await db_session.commit()

    event_id = f"evt_replay_{uuid.uuid4().hex[:12]}"
    invoice_event = {
        "id": event_id,
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "customer": cust_id,
                "amount_paid": 4900,
                "hosted_invoice_url": "https://stripe.com/invoice/123",
            }
        },
    }
    payload_bytes = json.dumps(invoice_event).encode("utf-8")

    # First delivery processes
    res1 = await billing_service.process_stripe_webhook(db_session, payload_bytes, None)
    assert res1["status"] == "processed"

    # 100 subsequent replays are all idempotent no-ops
    for _ in range(100):
        res = await billing_service.process_stripe_webhook(
            db_session, payload_bytes, None
        )
        assert res["status"] == "idempotent_duplicate"

    # Verify exactly 1 invoice was created
    invoices = await billing_service.get_billing_history(
        db_session, uuid.UUID(str(org.id))
    )
    assert len(invoices) == 1
    assert invoices[0].amount == 49.0


# ============================================================================
# MILESTONE 15: Complete End-to-End Billing Lifecycle Tests
# ============================================================================


@pytest.mark.asyncio
async def test_complete_billing_lifecycle_e2e(db_session: AsyncSession):
    billing_service = BillingService()
    org_service = OrganizationService()
    quota_service = QuotaService()

    # Step 1: Create organization (defaults to Starter tier)
    owner_id = uuid.uuid4()
    org = await org_service.create_organization(
        db_session, name="E2E Lifecycle Org", user_id=owner_id
    )
    org_uuid = uuid.UUID(str(org.id))
    ws_uuid = uuid.uuid4()

    ent1 = await billing_service.get_organization_entitlements(db_session, org_uuid)
    assert ent1["plan_name"] == "Starter"
    assert ent1["features"]["rag_evaluation"] is False

    # Step 2: Customer initiates checkout for Pro
    checkout_url = await billing_service.create_checkout_session(
        db_session, org_uuid, "Pro"
    )
    assert checkout_url is not None
    assert (await billing_service.get_active_subscription(db_session, org_uuid)) is None

    # Step 3: Webhook confirms checkout completion
    stripe_sub_id = f"sub_e2e_{uuid.uuid4().hex[:12]}"
    stripe_cust_id = f"cus_e2e_{uuid.uuid4().hex[:12]}"
    checkout_event = {
        "id": f"evt_checkout_{uuid.uuid4().hex[:12]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": stripe_cust_id,
                "subscription": stripe_sub_id,
                "metadata": {
                    "organization_id": str(org_uuid),
                    "plan_name": "Pro",
                },
            }
        },
    }
    res_webhook = await billing_service.process_stripe_webhook(
        db_session, json.dumps(checkout_event).encode("utf-8"), None
    )
    assert res_webhook["status"] == "processed"

    # Step 4: Organization is now upgraded to Pro with premium entitlements
    ent2 = await billing_service.get_organization_entitlements(db_session, org_uuid)
    assert ent2["plan_name"] == "Pro"
    assert ent2["features"]["rag_evaluation"] is True
    assert (
        await billing_service.has_entitlement(db_session, org_uuid, "rag_evaluation")
        is True
    )

    # Step 5: Quota reservation and usage metering within Pro limits (1,000 evals)
    await quota_service.reserve_quota(
        db_session, org_uuid, ws_uuid, "evaluations", 50.0
    )
    await quota_service.record_usage(db_session, org_uuid, ws_uuid, "evaluations", 50.0)

    # Step 6: Customer launches Customer Portal (state remains active Pro)
    portal_url = await billing_service.create_customer_portal_session(
        db_session, org_uuid
    )
    assert portal_url is not None

    # Step 7: Payment failure occurs (subscription status transitions to past_due)
    fail_event = {
        "id": f"evt_fail_{uuid.uuid4().hex[:12]}",
        "type": "invoice.payment_failed",
        "data": {"object": {"customer": stripe_cust_id}},
    }
    await billing_service.process_stripe_webhook(
        db_session, json.dumps(fail_event).encode("utf-8"), None
    )
    sub_past_due = await billing_service.get_active_subscription(db_session, org_uuid)
    assert sub_past_due is None  # past_due is not active

    # Step 8: Subscription canceled / deleted (entitlements immediately fail closed back to Starter)
    del_event = {
        "id": f"evt_del_{uuid.uuid4().hex[:12]}",
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": stripe_sub_id}},
    }
    await billing_service.process_stripe_webhook(
        db_session, json.dumps(del_event).encode("utf-8"), None
    )

    ent3 = await billing_service.get_organization_entitlements(db_session, org_uuid)
    assert ent3["plan_name"] == "Starter"
    assert ent3["features"]["rag_evaluation"] is False
    with pytest.raises(TenantAccessViolationException, match="Upgrade required"):
        await billing_service.require_entitlement(
            db_session, org_uuid, "rag_evaluation"
        )
