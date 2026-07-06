class AnalyticsException(Exception):
    """Base exception for analytics errors."""

    pass


class ReportNotFoundException(AnalyticsException):
    """Raised when a report is not found."""

    def __init__(self, report_id: str):
        super().__init__(f"Report with ID '{report_id}' not found.")


class InsightNotFoundException(AnalyticsException):
    """Raised when an insight is not found."""

    def __init__(self, insight_id: str):
        super().__init__(f"Insight with ID '{insight_id}' not found.")


class AlertNotFoundException(AnalyticsException):
    """Raised when an alert is not found."""

    def __init__(self, alert_id: str):
        super().__init__(f"Alert with ID '{alert_id}' not found.")
