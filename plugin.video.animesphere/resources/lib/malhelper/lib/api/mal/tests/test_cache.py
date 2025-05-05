"""
Tests for the Cache class
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from ..cache import Cache

class TestCache(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for cache tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache = Cache(cache_dir=self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()

    def test_cache_creation(self):
        """Test cache directory creation"""
        self.assertTrue(os.path.exists(self.cache.cache_dir))

    def test_cache_get_nonexistent(self):
        """Test getting non-existent cache"""
        result = self.cache.get('nonexistent_key')
        self.assertIsNone(result)

    def test_cache_get_expired(self):
        """Test getting expired cache"""
        # Create an expired cache file
        cache_file = os.path.join(self.cache.cache_dir, 'expired_key.json')
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': (datetime.now() - timedelta(seconds=self.cache.cache_time + 1)).isoformat(),
                'data': {'test': 'data'}
            }, f)

        result = self.cache.get('expired_key')
        self.assertIsNone(result)

    def test_cache_get_valid(self):
        """Test getting valid cache"""
        # Create a valid cache file
        cache_file = os.path.join(self.cache.cache_dir, 'valid_key.json')
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': {'test': 'data'}
            }, f)

        result = self.cache.get('valid_key')
        self.assertEqual(result, {'test': 'data'})

    def test_cache_get_expired(self):
        """Test getting expired cache"""
        # Create an expired cache file
        cache_file = os.path.join(self.cache.cache_dir, 'expired_key.json')
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': (datetime.now() - timedelta(seconds=self.cache.cache_time + 1)).isoformat(),
                'data': {'test': 'data'}
            }, f)

        result = self.cache.get('expired_key')
        self.assertIsNone(result)

    def test_cache_get_corrupted(self):
        """Test getting corrupted cache"""
        # Create a corrupted cache file
        cache_file = os.path.join(self.cache.cache_dir, 'corrupted_key.json')
        with open(cache_file, 'w') as f:
            f.write('invalid json')

        with patch('logging.warning') as mock_warning:
            result = self.cache.get('corrupted_key')
            self.assertIsNone(result)
            mock_warning.assert_called()
            self.assertFalse(os.path.exists(cache_file))  # Cache file should be deleted

    def test_cache_get_error(self):
        """Test getting cache with error"""
        # Create a cache file that will cause an error when reading
        cache_file = os.path.join(self.cache.cache_dir, 'error_key.json')
        with open(cache_file, 'w') as f:
            f.write('valid json')

        with patch('json.load', side_effect=Exception('Test error')):
            with patch('logging.error') as mock_error:
                result = self.cache.get('error_key')
                self.assertIsNone(result)
                mock_error.assert_called()

    def test_cache_set(self):
        """Test setting cache"""
        self.cache.set('test_key', {'test': 'data'})
        cache_file = os.path.join(self.cache.cache_dir, 'test_key.json')
        self.assertTrue(os.path.exists(cache_file))

        with open(cache_file, 'r') as f:
            data = json.load(f)
            self.assertIn('timestamp', data)
            self.assertIn('data', data)
            self.assertEqual(data['data'], {'test': 'data'})

    def test_cache_set_error(self):
        """Test setting cache with error"""
        with patch('json.dump', side_effect=Exception('Test error')):
            with patch('logging.error') as mock_error:
                self.cache.set('error_key', {'test': 'data'})
                mock_error.assert_called()

    def test_cache_clear_specific(self):
        """Test clearing specific cache"""
        # Create a cache file
        cache_file = os.path.join(self.cache.cache_dir, 'test_key.json')
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': {'test': 'data'}
            }, f)

        self.assertTrue(os.path.exists(cache_file))
        self.cache.clear('test_key')
        self.assertFalse(os.path.exists(cache_file))

    def test_cache_clear_nonexistent(self):
        """Test clearing non-existent cache"""
        self.cache.clear('nonexistent_key')  # Should not raise an error

    def test_cache_clear_error(self):
        """Test clearing cache with error"""
        # Create a cache file
        cache_file = os.path.join(self.cache.cache_dir, 'error_key.json')
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': {'test': 'data'}
            }, f)

        with patch('os.remove', side_effect=Exception('Test error')):
            with patch('logging.error') as mock_error:
                self.cache.clear('error_key')
                mock_error.assert_called()

    def test_cache_get_corrupted(self):
        """Test getting corrupted cache"""
        # Create a corrupted cache file
        cache_file = os.path.join(self.cache.cache_dir, 'corrupted_key.json')
        with open(cache_file, 'w') as f:
            f.write('invalid json')

        with patch('logging.warning') as mock_warning:
            result = self.cache.get('corrupted_key')
            self.assertIsNone(result)
            mock_warning.assert_called()

    def test_cache_exists(self):
        """Test cache exists check"""
        # Create a cache file
        cache_file = os.path.join(self.cache.cache_dir, 'test_key.json')
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'data': {'test': 'data'}
            }, f)

        self.assertTrue(self.cache.exists('test_key'))
        self.assertFalse(self.cache.exists('nonexistent_key'))

    def test_cache_exists_error(self):
        """Test cache exists with error"""
        with patch('os.path.exists', side_effect=OSError):
            with patch('logging.error') as mock_error:
                result = self.cache.exists('test_key')
                self.assertFalse(result)
                mock_error.assert_called()

if __name__ == '__main__':
    unittest.main()
