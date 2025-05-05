import json
from datetime import datetime, timedelta
import os
import logging

class Cache:
    def __init__(self, cache_dir='cache', cache_time=3600):
        """Initialize cache with configurable directory and time"""
        self.cache_dir = cache_dir
        self.cache_time = cache_time
        self._ensure_cache_dir()

    def get(self, key):
        """Get cached data for a key"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r') as f:
                data = json.load(f)
                cache_time = datetime.fromisoformat(data['timestamp'])
                if cache_time > datetime.now() - timedelta(seconds=self.cache_time):
                    return data['data']
        except Exception as e:
            logging.error(f"Error getting cache: {str(e)}")
        return None

    def exists(self, key):
        """Check if cache file exists"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            return os.path.exists(cache_file)
        except Exception as e:
            logging.error(f"Error checking cache: {str(e)}")
            return False

    def set(self, key, data):
        """Set cached data for a key"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f)
        except Exception as e:
            logging.error(f"Error setting cache: {str(e)}")

    def clear(self, key=None):
        """Clear cache for a specific key or all keys"""
        try:
            if key:
                cache_file = os.path.join(self.cache_dir, f"{key}.json")
                if os.path.exists(cache_file):
                    os.remove(cache_file)
            else:
                for file in os.listdir(self.cache_dir):
                    if file.endswith('.json'):
                        os.remove(os.path.join(self.cache_dir, file))
        except Exception as e:
            logging.error(f"Error clearing cache: {str(e)}")

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Error creating cache directory: {str(e)}")
