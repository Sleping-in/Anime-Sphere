"""
Constants for the MyAnimeList API
"""

# Base URL for the MyAnimeList API
API_BASE_URL = "https://api.myanimelist.net/v2"

# API version
API_VERSION = "v2"

# Default timeouts
DEFAULT_TIMEOUT = 10  # seconds

# Rate limiting
RATE_LIMIT_RESET = 60  # seconds
RATE_LIMIT_WINDOW = 900  # seconds (15 minutes)
RATE_LIMIT_REQUESTS = 900  # maximum requests in window

# Cache durations
CACHE_DURATION = {
    'anime_details': 86400,  # 24 hours
    'seasonal_anime': 3600,  # 1 hour
    'studio_anime': 3600,    # 1 hour
    'recently_watched': 300  # 5 minutes
}
