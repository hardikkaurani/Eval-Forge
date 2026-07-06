class EnterpriseBaseException(Exception):
    """Base exception for all enterprise SaaS errors."""

    pass


class TenantAccessViolationException(EnterpriseBaseException):
    """Raised when a user attempts to access a resource belonging to a different tenant/organization."""

    pass


class PlanQuotaExceededException(EnterpriseBaseException):
    """Raised when an organization or workspace attempts to exceed their assigned quota limits."""

    pass


class BillingGatewayException(EnterpriseBaseException):
    """Raised when an error occurs during payment processing or subscription synchronization."""

    pass


class InvitationExpiredOrInvalidException(EnterpriseBaseException):
    """Raised when an invitation link has expired or has already been accepted/revoked."""

    pass


class CustomDomainCollisionException(EnterpriseBaseException):
    """Raised when attempting to configure a custom domain that is already registered to another tenant."""

    pass
