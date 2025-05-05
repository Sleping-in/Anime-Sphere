import requests
import json
from datetime import datetime, timedelta
import os
import time
import base64
import hashlib
import webbrowser
from urllib.parse import urlencode
from typing import List, Dict, Optional
import logging
from enum import Enum
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Error codes
class ErrorCode(Enum):
    AUTH_ERROR = 1
    NETWORK_ERROR = 2
    API_ERROR = 3
    CACHE_ERROR = 4
    CONFIG_ERROR = 5

@dataclass
class APIErrorDetails:
    code: ErrorCode
    message: str
    details: Dict = None

# Default timeout for API requests in seconds
DEFAULT_TIMEOUT = 10

# API request retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Try to import Kodi modules
try:
    import xbmc
    import xbmcaddon
    import xbmcgui
    import xbmcplugin
except ImportError:
    # If running outside Kodi, use stubs
    from kodi_stubs import xbmc, xbmcaddon, xbmcgui, xbmcplugin

from .settings import get_setting
from .cache import Cache
from .constants import API_BASE_URL

class APIError(Exception):
    """Exception raised for API-related errors"""
    def __init__(self, message, **kwargs):
        self.message = message
        self.status_code = kwargs.get('status_code', None)
        self.response = kwargs.get('response', None)
        self.key = kwargs.get('key', None)
        super().__init__(self.message)

class MyAnimeList:
    """Client for the MyAnimeList API"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, 
                 auto_authorize: bool = True):
        """Initialize the MyAnimeList API client

        Args:
            client_id: MAL OAuth2 client ID
            client_secret: MAL OAuth2 client secret
            auto_authorize: Whether to automatically authorize on creation
        """
        self.client_id = client_id or get_setting('client_id')
        self.client_secret = client_secret or get_setting('client_secret')
        self.auto_authorize = auto_authorize
        self.access_token = None
        self.refresh_token = None
        self.token_expires = 0
        self.base_url = API_BASE_URL
        self.cache = Cache()
        
        if auto_authorize:
            self._authorize()
        
        # Load cached tokens if available
        if self.cache.exists('tokens.json'):
            tokens = self.cache.get('tokens.json')
            if tokens:
                self.access_token = tokens['access_token']
                self.refresh_token = tokens.get('refresh_token', self.refresh_token)
                self.token_expires = tokens.get('expires_in', 0)
                
    def _refresh_token(self) -> bool:
        """Refresh the access token using the refresh token
        
        Returns:
            bool: True if token refresh was successful, False otherwise
        """
        if not self.refresh_token:
            logging.error("No refresh token available")
            return False

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(
                "https://myanimelist.net/v1/oauth2/token",
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=payload
            )
            
            if response.status_code == 400:
                error_data = response.json()
                logging.error(f"Token refresh failed: {error_data.get('message', 'Invalid refresh token')}")
                return False
                
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token', self.refresh_token)
            self.token_expires = time.time() + token_data['expires_in']
            
            # Save to cache
            self.cache.save_tokens(
                self.access_token,
                self.refresh_token,
                self.token_expires
            )
            
            logging.info("Token refresh successful")
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Token refresh failed: {str(e)}")
            return False

    def _authorize(self):
        """Authorize with MyAnimeList API"""
        if not self.client_id or not self.client_secret:
            raise ValueError("Client ID and secret are required")

        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.request(
                'POST',
                self.base_url + '/auth/token',
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if 'access_token' not in data:
                logging.error(f"Authorization failed: {data}")
                return False
                
            self.access_token = data['access_token']
            self.refresh_token = data.get('refresh_token')
            self.token_expires = time.time() + data['expires_in']
            
            # Cache the tokens
            self.cache.set('tokens.json', {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_in': self.token_expires
            })
            
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Authorization failed: {str(e)}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {"X-MAL-CLIENT-ID": self.client_id}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _make_request(self, url: str, method: str = "GET", params: Optional[Dict] = None,
                          data: Optional[Dict] = None) -> Dict:
        """Make a request to the MyAnimeList API with retry logic

        Args:
            url: The URL to request
            method: The HTTP method to use
            params: Query parameters for the request
            data: Data for POST/PUT requests

        Returns:
            The parsed JSON response

        Raises:
            APIError: If the request fails or returns an error
        """
        retry_count = 0
        last_error = None

        while retry_count < MAX_RETRIES:
            try:
                headers = self._get_headers()
                
                logger.debug(f"Making {method} request to {url}")
                logger.debug(f"Request params: {params}")
                logger.debug(f"Request data: {data}")
                
                # Add timeout to request
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=DEFAULT_TIMEOUT
                )
                
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                
                # Check for rate limiting
                if response.status_code == 429:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    if reset_time:
                        wait_time = reset_time - int(time.time())
                        if wait_time > 0:
                            logger.warning(f"Rate limit hit. Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                    else:
                        time.sleep(RATE_LIMIT_RESET)
                    
                    # Retry the request
                    retry_count += 1
                    continue
                
                # Check for authentication errors
                if response.status_code == 401:
                    if self.refresh_token:
                        logger.info("Refreshing access token...")
                        if self._refresh_token():
                            logger.info("Token refreshed successfully")
                            return self._make_request(url, method, params, data)
                        else:
                            raise APIError(
                                "Failed to refresh access token",
                                details={"error": "refresh_failed"}
                            )
                    else:
                        raise APIError(
                            "Authentication required",
                            details={"error": "auth_required"}
                        )
                
                response.raise_for_status()
                
                try:
                    json_response = response.json()
                    logger.debug(f"Response data: {json_response}")
                    return json_response
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON response: {str(e)}")
                    raise APIError(
                        f"Invalid JSON response: {str(e)}",
                        details={"error": "invalid_json", "raw": response.text}
                    )
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error: {str(e)}")
                last_error = e
                retry_count += 1
                time.sleep(RETRY_DELAY * retry_count)
                
        if last_error:
            raise APIError(
                f"Failed after {MAX_RETRIES} retries: {str(last_error)}",
            )
            
    def get_mal_id(self, title: str) -> int:
        """Get MAL ID from title

        Args:
            title: The title to search for

        Returns:
            The MAL ID of the found anime
        """
        response = requests.request(
            'GET',
            f'{self.base_url}/anime',
            params={'q': title, 'limit': 1}
        )
        response.raise_for_status()
        data = response.json()
        return data['data'][0]['node']['id']

    def add_to_watchlist(self, anime_id: int) -> Dict:
        """Add anime to watchlist

        Args:
            anime_id: The ID of the anime

        Returns:
            The updated list status
        """
        return self.update_list_status(anime_id, status='plan_to_watch')

    def update_progress(self, anime_id: int, episodes_watched: int) -> Dict:
        """Update watched episode count

        Args:
            anime_id: The ID of the anime
            episodes_watched: The number of episodes watched

        Returns:
            Dictionary containing the updated list status
        """
        return self.update_list_status(anime_id, num_watched_episodes=episodes_watched)

    def get_anime_ranking(self, ranking_type: str = 'all', limit: int = 100) -> Dict:
        """Get the anime ranking

        Args:
            ranking_type: Type of ranking (all, airing, upcoming, etc.)
            limit: Maximum number of results to return

        Returns:
            Dictionary containing anime ranking data
        """
        url = f'{self.base_url}/anime/ranking'
        params = {
            'ranking_type': ranking_type,
            'limit': limit
        }
        return self._make_request(url, params=params)

    def get_seasonal_anime(self, year: int, season: str) -> Dict:
        """Get seasonal anime

        Args:
            year: The year of the season
            season: The season (spring, summer, fall, winter)

        Returns:
            The seasonal anime data
        """
        url = f'{self.base_url}/anime/season'
        params = {
            'year': year,
            'season': season,
            'limit': 100
        }
        return self._make_request(url, params=params)

    def get_watch_status(self, anime_id: int) -> Dict:
        """Get the watch status of an anime

        Args:
            anime_id: The MyAnimeList ID of the anime

        Returns:
            Dictionary containing watch status information
        """
        url = f'{self.base_url}/anime/{anime_id}'
        return self._make_request(url, params={'fields': 'my_list_status'})

    def get_recently_watched(self) -> List[Dict]:
        """Get recently watched anime

        Returns:
            List of recently watched anime
        """
        url = f'{self.base_url}/users/@me/animelist'
        params = {'fields': 'my_list_status'}
        return self._make_request(url, params=params)['data']

    def update_list_status(self, anime_id: int, **kwargs) -> Dict:
        """Update the list status for an anime

        Args:
            anime_id: The ID of the anime
            **kwargs: Additional status parameters

        Returns:
            The updated list status
        """
        url = f'{self.base_url}/anime/{anime_id}/my_list_status'
        return self._make_request(url, method='PUT', data=kwargs)

    def get_episode_history(self, anime_id: int) -> List[Dict]:
        """Get episode history for an anime

        Args:
            anime_id: The MyAnimeList ID of the anime

        Returns:
            List of episode history entries
        """
        data = self.get_watch_status(anime_id)
        return data['my_list_status']['episode_history']

    def get_next_episodes(self) -> List[Dict]:
        """Get next episodes to watch

        Returns:
            List of next episodes to watch
        """
        response = self._make_request(
            f'{self.base_url}/anime',
            params={'status': 'watching', 'limit': 100}
        )
        next_eps = []
        for item in response.get('data', []):
            node = item['node']
            status = node.get('my_list_status', {})
            next_eps.append({
                'id': node['id'],
                'episode': status.get('num_episodes_watched', 0) + 1
            })
        return next_eps

    def get_episode_progress(self, anime_id: int) -> Dict:
        """Get detailed episode progress

        Args:
            anime_id: The MyAnimeList ID of the anime

        Returns:
            Dictionary containing episode progress information
        """
        data = self.get_watch_status(anime_id)
        status = data['my_list_status']
        return {
            'num_watched_episodes': status.get('num_watched_episodes'),
            'total_episodes': status.get('total_episodes'),
            'next_episode': status.get('next_episode'),
            'episode_history': status.get('episode_history')
        }

    def get_anime_details(self, anime_id: int) -> Dict:
        """Get detailed information about an anime

        Args:
            anime_id: The MyAnimeList ID of the anime

        Returns:
            Dictionary containing anime details
        """
        url = f'{self.base_url}/anime/{anime_id}'
        return self._make_request(url, params={'fields': 'recommendations'})

    def get_similar_anime(self, mal_id: int, limit: int = 10) -> List[Dict]:
        """Get similar anime recommendations

        Args:
            mal_id: The MyAnimeList ID of the anime
            limit: Maximum number of recommendations to return

        Returns:
            List[Dict]: List of dictionaries containing anime recommendations
        """
        try:
            anime = self.get_anime_details(mal_id)
            if not anime or not anime.get('recommendations'):
                return []
            
            return [{
                'id': rec.get('node', {}).get('id'),
                'title': rec.get('node', {}).get('title'),
                'main_picture': rec.get('node', {}).get('main_picture'),
                'recommendation_count': rec.get('node', {}).get('recommendation_count', 0)
            } for rec in anime.get('recommendations', [])[:limit]]
        except APIError as e:
            logging.error(f"Error getting similar anime: {str(e)}")
            return []

    def get_studio_anime(self, studio_id: int, limit: int = 10) -> List[Dict]:
        """
        Get anime from a specific studio.

        Args:
            studio_id (int): The ID of the studio.
            limit (int): Maximum number of anime to return.

        Returns:
            List[Dict]: List of dictionaries containing anime data.
        """
        try:
            url = f"{self.base_url}/anime/studios/{studio_id}/anime"
            
            fields = [
                'id', 'title', 'main_picture', 'alternative_titles',
                'start_date', 'end_date', 'synopsis', 'mean', 'rank',
                'popularity', 'num_list_users', 'num_scoring_users',
                'nsfw', 'created_at', 'updated_at', 'media_type',
                'status', 'genres', 'num_episodes'
            ]
            
            params = {
                'fields': ','.join(fields),
                'limit': limit
            }
            
            response = self._make_request(url, params=params)
            if not response or not response.get('data'):
                return []
            
            return [{
                'id': anime.get('node', {}).get('id'),
                'title': anime.get('node', {}).get('title'),
                'main_picture': anime.get('node', {}).get('main_picture'),
                'alternative_titles': anime.get('node', {}).get('alternative_titles'),
                'start_date': anime.get('node', {}).get('start_date'),
                'end_date': anime.get('node', {}).get('end_date'),
                'synopsis': anime.get('node', {}).get('synopsis'),
                'mean': anime.get('node', {}).get('mean'),
                'rank': anime.get('node', {}).get('rank'),
                'popularity': anime.get('node', {}).get('popularity'),
                'num_list_users': anime.get('node', {}).get('num_list_users'),
                'num_scoring_users': anime.get('node', {}).get('num_scoring_users'),
                'nsfw': anime.get('node', {}).get('nsfw'),
                'created_at': anime.get('node', {}).get('created_at'),
                'updated_at': anime.get('node', {}).get('updated_at'),
                'media_type': anime.get('node', {}).get('media_type'),
                'status': anime.get('node', {}).get('status'),
                'genres': anime.get('node', {}).get('genres'),
                'num_episodes': anime.get('node', {}).get('num_episodes')
            } for anime in response.get('data', [])]
        except APIError as e:
            logging.error(f"Error getting studio anime: {str(e)}")
            return []
