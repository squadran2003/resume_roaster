from rest_framework.throttling import UserRateThrottle


class AIAnalysisThrottle(UserRateThrottle):
    scope = "ai_endpoints"
