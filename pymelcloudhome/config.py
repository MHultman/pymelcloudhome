"""Configuration constants for pymelcloudhome."""

# API Configuration
BASE_URL = "https://www.melcloudhome.com/api/"
LOGIN_URL = "https://www.melcloudhome.com/bff/login?returnUrl=/dashboard"
DASHBOARD_URL_PATTERN = "**/dashboard"

# Default timeouts and settings
DEFAULT_CACHE_DURATION_MINUTES = 5
LOGIN_TIMEOUT_MILLISECONDS = 30000

# HTTP Headers
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "x-csrf": "1",
    "user-agent": DEFAULT_USER_AGENT,
}

# Device types
DEVICE_TYPE_AIR_TO_AIR = "ataunit"
DEVICE_TYPE_AIR_TO_WATER = "atwunit"

# API endpoints
ENDPOINT_USER_CONTEXT = "user/context"