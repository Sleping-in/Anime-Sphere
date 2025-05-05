import os
import json
import time
import xbmc
import xbmcvfs
from pathlib import Path

class Cache:
    def __init__(self):
        self.cache_dir = xbmc.translatePath('special://temp/mal_helper_cache')
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, key):
        """Get cache file path for a key"""
        return os.path.join(self.cache_dir, f'{key}.json')

    def set(self, key, value, ttl=3600):
        """Set a value in cache with TTL"""
        cache_path = self._get_cache_path(key)
        cache_data = {
            'value': value,
            'expires': time.time() + ttl
        }
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)

    def get(self, key):
        """Get a value from cache"""
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return None

        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        if cache_data['expires'] < time.time():
            self.delete(key)
            return None

        return cache_data['value']

    def exists(self, key):
        """Check if a key exists in cache"""
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return False

        with open(cache_path, 'r') as f:
            cache_data = json.load(f)

        return cache_data['expires'] > time.time()

    def delete(self, key):
        """Delete a key from cache"""
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            os.remove(cache_path)

    def clear(self):
        """Clear all cache"""
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, file))

    def size(self):
        """Get cache size in bytes"""
        total_size = 0
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                total_size += os.path.getsize(os.path.join(self.cache_dir, file))
        return total_size

    def stats(self):
        """Get cache statistics"""
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        return {
            'total_files': len(cache_files),
            'total_size': self.size(),
            'cache_dir': self.cache_dir
        }
