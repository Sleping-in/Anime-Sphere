"""MyAnimeList API package

This package provides integration with the MyAnimeList API, including:
- Authentication handling
- Cache management
- API request handling
- Error handling
"""

from .api import MyAnimeList, APIError
from .cache import Cache
from .settings import get_setting

__all__ = ['MyAnimeList', 'APIError', 'Cache', 'get_setting']