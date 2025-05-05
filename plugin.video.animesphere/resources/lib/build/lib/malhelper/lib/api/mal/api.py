import requests
import json
from datetime import datetime, timedelta
import os
import time
import logging

from .settings import get_setting
from .cache import Cache

class APIError(Exception):
    """Exception raised for API-related errors"""
    def __init__(self, message, **kwargs):
        self.message = message
        self.status_code = kwargs.get('status_code', None)
        self.response = kwargs.get('response', None)
        self.key = kwargs.get('key', None)
        super().__init__(self.message)

class MyAnimeList:
    def __init__(self):
        self.base_url = "https://api.myanimelist.net/v2"
        self.client_id = 'd9abb9cbc9871ea3d55f1eb605f3e166'
        self.client_secret = '5179742b310a90862424cedf9e969c3de5ece34638962b2500ea98b3ef1afd0c'
        self.username = 'E_Senshi'
        self.password = 'Moh55378076'
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        self.cache = Cache()
        self._get_tokens()

    def _get_tokens(self):
        """Get access and refresh tokens"""
        try:
            url = "https://api.myanimelist.net/v2/auth/token"
            data = {
                'grant_type': 'password',
                'username': self.username,
                'password': self.password,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code != 200:
                error_msg = f"Authentication failed: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', 'No error message')}"
                    except json.JSONDecodeError:
                        error_msg += f" - {response.text}"
                raise APIError(error_msg)
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires = time.time() + token_data['expires_in']
            return True
        except Exception as e:
            raise APIError(f"Failed to get tokens: {str(e)}")

    def _save_tokens(self):
        """Save tokens to settings"""
        try:
            import xbmcaddon
            addon = xbmcaddon.Addon()
            addon.setSetting('mal_access_token', self.access_token)
            addon.setSetting('mal_refresh_token', self.refresh_token)
            addon.setSetting('mal_token_expires', str(self.token_expires))
        except ImportError:
            # If running in test environment, do nothing
            pass
        except Exception as e:
            logging.error(f"Error saving tokens: {str(e)}")

    def _refresh_token(self):
        """Refresh the access token using the refresh token"""
        try:
            url = "https://api.myanimelist.net/v2/auth/token"
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            self.token_expires = int(time.time()) + token_data['expires_in']
            
            # Save tokens to settings
            self._save_tokens()
            
            return True
        except Exception as e:
            logging.error(f"Error refreshing token: {str(e)}")
            return False

    def _get_headers(self):
        """Get request headers"""
        if self._is_token_expired():
            self._refresh_token()
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'X-MAL-Client-ID': self.client_id
        }

    def _is_token_expired(self):
        """Check if the access token is expired"""
        if self.token_expires is None:
            return True
        return self.token_expires < int(time.time())

    def _make_request(self, url, params=None, method='GET', data=None):
        """Make API request with error handling"""
        try:
            headers = self._get_headers()
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data
            )
            
            if response.status_code == 401:
                # Try to refresh token
                self._get_tokens()
                headers = self._get_headers()
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data
                )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f'API request failed: {str(e)}')

    def get_anime_details(self, mal_id):
        """Get anime details with caching"""
        cache_key = f'anime_details_{mal_id}'
        if self.cache.exists(cache_key):
            return self.cache.get(cache_key)

        url = f"{self.base_url}/anime/{mal_id}"
        fields = [
            'id', 'title', 'main_picture', 'alternative_titles',
            'start_date', 'end_date', 'synopsis', 'mean', 'rank',
            'popularity', 'num_list_users', 'num_scoring_users',
            'nsfw', 'created_at', 'updated_at', 'media_type',
            'status', 'genres', 'num_episodes',
            'start_season', 'broadcast', 'source',
            'average_episode_duration', 'rating', 'pictures',
            'background', 'related_anime', 'recommendations',
            'studios', 'characters', 'statistics',
            'my_list_status'
        ]
        params = {'fields': ','.join(fields)}
        
        logging.debug(f"Getting anime details for ID: {mal_id}")
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Request params: {params}")
        
        result = self._make_request(url, params=params)
        logging.debug(f"API response: {result}")
        
        self.cache.set(cache_key, result)
        return result

    def get_anime_ranking(self, ranking_type='all', limit=100):
        url = f"{self.base_url}/anime/ranking"
        fields = [
            'id', 'title', 'main_picture', 'alternative_titles',
            'start_date', 'end_date', 'synopsis', 'mean', 'rank',
            'popularity', 'num_list_users', 'num_scoring_users',
            'nsfw', 'created_at', 'updated_at', 'media_type',
            'status', 'genres', 'num_episodes',
            'start_season', 'broadcast', 'source',
            'average_episode_duration', 'rating', 'studios'
        ]
        params = {
            'ranking_type': ranking_type,
            'limit': limit,
            'fields': ','.join(fields)
        }
        return self._make_request(url, params=params)

    def get_seasonal_anime(self, year=None, season=None, sort=None, limit=100):
        url = f"{self.base_url}/anime/season"
        fields = [
            'id', 'title', 'main_picture', 'alternative_titles',
            'start_date', 'end_date', 'synopsis', 'mean', 'rank',
            'popularity', 'num_list_users', 'num_scoring_users',
            'nsfw', 'created_at', 'updated_at', 'media_type',
            'status', 'genres', 'num_episodes',
            'start_season', 'broadcast', 'source',
            'average_episode_duration', 'rating', 'studios'
        ]
        params = {
            'limit': limit,
            'fields': ','.join(fields)
        }
        if year:
            params['year'] = year
        if season:
            params['season'] = season
        if sort:
            params['sort'] = sort
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_mal_id(self, **kwargs):
        """Get MAL ID from various identifiers"""
        if 'mal_id' in kwargs:
            return kwargs['mal_id']
        
        # Add logic to get MAL ID from other identifiers
        # This would require implementing search functionality
        return None

    def add_to_watchlist(self, mal_id, status='plan_to_watch'):
        """Add anime to watchlist"""
        return self.update_list_status(mal_id, status=status)

    def update_progress(self, mal_id, episode):
        """Update watched episode count"""
        return self.update_list_status(mal_id, num_watched_episodes=episode)

    def get_watch_status(self, mal_id):
        """Get current watch status for an anime"""
        details = self.get_anime_details(mal_id)
        return details.get('my_list_status', {})

    def get_episode_history(self, mal_id):
        """Get episode viewing history"""
        status = self.get_watch_status(mal_id)
        return status.get('episode_history', [])

    def get_recently_watched(self, user_id='@me', limit=10):
        """Get recently watched anime"""
        return self.get_user_anime_list(user_id, status='watching', sort='list_score', limit=limit)

    def get_next_episodes(self, user_id='@me', limit=10):
        """Get next episodes to watch"""
        watching = self.get_user_anime_list(user_id, status='watching', limit=limit)
        return [anime for anime in watching.get('data', []) if anime.get('my_list_status', {}).get('num_watched_episodes', 0) < anime.get('num_episodes', 0)]

    def update_list_status(self, mal_id, **kwargs):
        """Update anime list status with basic parameters"""
        url = f"{self.base_url}/anime/{mal_id}/my_list_status"
        valid_fields = [
            'status', 'score', 'num_watched_episodes',
            'start_date', 'finish_date', 'episode_history',
            'episode_progress'
        ]

    def get_episode_progress(self, mal_id):
        """Get detailed episode progress"""
        status = self.get_watch_status(mal_id)
        return {
            'current_episode': status.get('num_watched_episodes', 0),
            'total_episodes': status.get('episode_progress', {}).get('total', 0),
            'next_episode': status.get('episode_progress', {}).get('next', None),
            'history': status.get('episode_history', [])
        }

    def get_similar_anime(self, mal_id, limit=10):
        """Get similar anime recommendations"""
        anime = self.get_anime_details(mal_id)
        similar = anime.get('recommendations', [])
        return similar[:limit]

    def get_studio_anime(self, studio_id, limit=10):
        """Get anime from a specific studio"""
        url = f"{self.base_url}/studios/{studio_id}/anime"
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
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()
        
        data = {k: v for k, v in kwargs.items() if k in valid_fields}
        if not data:
            raise ValueError("At least one valid field must be provided")
        response = requests.put(url, headers=self._get_headers(), json=data)
        response.raise_for_status()
        return response.json()
