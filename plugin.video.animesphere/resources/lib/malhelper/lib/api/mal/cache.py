import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheError(Exception):
    """Exception raised for cache-related errors"""
    pass

class Cache:
    def __init__(self, cache_dir: str = None):
        """Initialize the cache system

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir or os.path.join(os.path.dirname(__file__), 'cache'))
        self._initialize_cache_dir()
        self._cleanup_old_cache()

    def _initialize_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create cache directory: {e}")
            raise CacheError(f"Failed to create cache directory: {e}")

    def _cleanup_old_cache(self) -> None:
        """Clean up expired cache files"""
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get('expires') and datetime.fromisoformat(data['expires']) < datetime.now():
                            cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to clean cache file {cache_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to clean cache: {e}")

    def exists(self, key: str) -> bool:
        """Check if a cache file exists

        Args:
            key: The cache key to check

        Returns:
            bool: True if cache file exists, False otherwise
        """
        cache_file = self.cache_dir / f"{key}.json"
        return cache_file.exists()

    def get(self, key: str) -> Optional[Dict]:
        """Get cached data with proper error handling

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found

        Raises:
            CacheError: If there's an error accessing the cache
        """
        try:
            cache_file = self.cache_dir / f'{key}.json'
            
            if not cache_file.exists():
                return None

            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check if cache is expired
            if data.get('expires') and datetime.fromisoformat(data['expires']) < datetime.now():
                self.delete(key)
                return None

            # Validate cache data
            if not isinstance(data.get('data'), dict):
                logger.warning(f"Invalid cache data format for key {key}")
                self.delete(key)
                return None

            return data.get('data')
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for cache {key}: {e}")
            self.delete(key)
            return None
        except Exception as e:
            logger.error(f"Cache error for key {key}: {e}")
            raise CacheError(f"Failed to get cache for {key}: {e}")

    def set(self, key: str, data: Dict, expire_seconds: int = 3600) -> None:
        """Set cached data with proper error handling

        Args:
            key: Cache key
            data: Data to cache
            expire_seconds: Cache expiration in seconds

        Raises:
            CacheError: If there's an error writing to cache
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Cache data must be a dictionary")

            cache_file = self.cache_dir / f'{key}.json'
            
            # Add expiration timestamp
            cache_data = {
                'data': data,
                'expires': (datetime.now() + timedelta(seconds=expire_seconds)).isoformat(),
                'created': datetime.now().isoformat(),
                'key': key
            }
            
            # Create parent directories if needed
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"Cached data for {key} with expiration {expire_seconds} seconds")
            
        except ValueError as e:
            logger.error(f"Invalid cache data: {e}")
            raise CacheError(f"Invalid cache data: {e}")
        except Exception as e:
            logger.error(f"Cache error for key {key}: {e}")
            raise CacheError(f"Failed to set cache for {key}: {e}")

    def delete(self, key: str) -> None:
        """Delete cached data with proper error handling

        Args:
            key: Cache key

        Raises:
            CacheError: If there's an error deleting cache
        """
        try:
            cache_file = self.cache_dir / f'{key}.json'
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"Deleted cache for {key}")
        except Exception as e:
            logger.error(f"Cache error for key {key}: {e}")
            raise CacheError(f"Failed to delete cache for {key}: {e}")

    def clear(self) -> None:
        """Clear all cached data with proper error handling

        Raises:
            CacheError: If there's an error clearing cache
        """
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete cache file {cache_file}: {e}")
            logger.debug("Cleared all cache files")
        except Exception as e:
            logger.error(f"Cache error: {e}")
            raise CacheError(f"Failed to clear cache: {e}")

    def get_all_keys(self) -> List[str]:
        """Get all cache keys

        Returns:
            List of cache keys
        """
        try:
            return [f.stem for f in self.cache_dir.glob('*.json')]
        except Exception as e:
            logger.error(f"Cache error: {e}")
            return []

    def get_cache_stats(self) -> Dict:
        """Get cache statistics

        Returns:
            Dictionary containing cache statistics
        """
        try:
            cache_files = list(self.cache_dir.glob('*.json'))
            return {
                'total_files': len(cache_files),
                'total_size': sum(f.stat().st_size for f in cache_files),
                'last_modified': max(f.stat().st_mtime for f in cache_files) if cache_files else 0
            }
        except Exception as e:
            logger.error(f"Cache error: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'last_modified': 0
            }

    def save_tokens(self, access_token, refresh_token, token_expires):
        """Save OAuth2 tokens to cache"""
        try:
            cache_file = os.path.join(self.cache_dir, 'tokens.json')
            with open(cache_file, 'w') as f:
                json.dump({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expires': token_expires,
                    'timestamp': datetime.now().isoformat()
                }, f)
        except Exception as e:
            logging.error(f"Error saving tokens: {str(e)}")

    def load_tokens(self):
        """Load OAuth2 tokens from cache"""
        try:
            cache_file = os.path.join(self.cache_dir, 'tokens.json')
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if datetime.fromisoformat(data['timestamp']) > datetime.now() - timedelta(seconds=self.cache_time):
                    return {
                        'access_token': data['access_token'],
                        'refresh_token': data['refresh_token'],
                        'token_expires': data['token_expires']
                    }
        except json.JSONDecodeError:
            # If cache file is corrupted, delete it
            try:
                os.remove(cache_file)
                logging.warning(f"Deleted corrupted cache file: {cache_file}")
            except Exception as e:
                logging.error(f"Error deleting corrupted cache file: {str(e)}")
        except Exception as e:
            logging.error(f"Error loading tokens: {str(e)}")
        return None

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Error creating cache directory: {str(e)}")
