"""API package"""

from .mal import MyAnimeList, APIError, Cache, get_setting

__all__ = ['MyAnimeList', 'APIError', 'Cache', 'get_setting']
