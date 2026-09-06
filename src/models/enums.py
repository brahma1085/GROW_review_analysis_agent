from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"

class PriorityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class TrendType(str, Enum):
    NEW = "new"
    GROWING = "growing"
    DECLINING = "declining"
    PERSISTENT = "persistent"

class CollectionStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"

class ReviewCategory(str, Enum):
    PRAISE = "praise"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    CUSTOMER_SUPPORT = "customer_support"
    PRICING_FEES = "pricing_fees"
    ACCOUNT_ISSUES = "account_issues"
    TRADING_INVESTING = "trading_investing"
    UI_UX = "ui_ux"
    SECURITY = "security"
    NOTIFICATIONS = "notifications"
    APP_UPDATE = "app_update"
    ONBOARDING_KYC = "onboarding_kyc"
    SPAM_SCAM = "spam_scam"
    OTHER = "other"
