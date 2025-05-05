"""
Tests for the OAuth2 authentication flow
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import builtins
import webbrowser
import time

from malhelper.lib.api.mal.api import MyAnimeList
from malhelper.lib.api.mal.cache import Cache

class TestOAuthFlow(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Set up test environment
        os.environ['KODI_CLIENT_ID'] = 'test_client_id'
        os.environ['KODI_CLIENT_SECRET'] = 'test_client_secret'
        
        # Create test cache directory
        self.test_cache_dir = 'test_cache'
        if not os.path.exists(self.test_cache_dir):
            os.makedirs(self.test_cache_dir)
            
        # Set up mock cache
        self.cache = Cache(self.test_cache_dir)
        self.cache.save_tokens('test_access_token', 'test_refresh_token', datetime.now().timestamp() + 3600)
        
        # Create API instance
        self.api = MyAnimeList('test_client_id', auto_authorize=False)

    def tearDown(self):
        """Clean up after tests"""
        # Clean up test cache directory
        if os.path.exists(self.test_cache_dir):
            for file in os.listdir(self.test_cache_dir):
                os.remove(os.path.join(self.test_cache_dir, file))
            os.rmdir(self.test_cache_dir)

    @patch('requests.post')
    @patch('builtins.input')
    @patch('webbrowser.open')
    def test_authorize_success(self, mock_open, mock_input, mock_post):
        """Test successful authorization"""
        # Mock response
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'access_token': 'test_access_token',
                'refresh_token': 'test_refresh_token',
                'expires_in': 3600
            }
        )
        
        # Mock user input
        mock_input.return_value = 'test_code'
        
        # Test authorization
        result = self.api.authorize()
        self.assertTrue(result)
        self.assertEqual(self.api.access_token, 'test_access_token')
        self.assertEqual(self.api.refresh_token, 'test_refresh_token')

    @patch('requests.post')
    @patch('builtins.input')
    @patch('webbrowser.open')
    def test_authorize_failure(self, mock_open, mock_input, mock_post):
        """Test failed authorization"""
        # Mock response
        mock_post.return_value = MagicMock(
            status_code=400,
            json=lambda: {
                'message': 'Invalid authorization code'
            }
        )
        
        # Mock user input
        mock_input.return_value = 'invalid_code'
        
        # Test authorization
        result = self.api.authorize()
        self.assertFalse(result)
        self.assertIsNone(self.api.access_token)
        self.assertIsNone(self.api.refresh_token)

    @patch('requests.post')
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh"""
        # Mock response
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                'access_token': 'new_access_token',
                'refresh_token': 'new_refresh_token',
                'expires_in': 3600
            }
        )
        
        # Create API instance with expired token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'expired_token'
        api.refresh_token = 'test_refresh_token'
        api.token_expires = datetime.now().timestamp() - 3600
        
        # Test token refresh
        result = api._refresh_token()
        self.assertTrue(result)
        self.assertEqual(api.access_token, 'new_access_token')
        self.assertEqual(api.refresh_token, 'new_refresh_token')

    @patch('requests.post')
    def test_refresh_token_failure(self, mock_post):
        """Test failed token refresh with JSON error response"""
        # Mock failed refresh response with JSON error
        mock_post.return_value = MagicMock(
            status_code=400,
            json=lambda: {
                'message': 'Invalid refresh token'
            }
        )
        
        # Create API instance with expired token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'expired_token'
        api.refresh_token = 'test_refresh_token'
        api.token_expires = datetime.now().timestamp() - 3600
        
        # Test token refresh
        result = api._refresh_token()
        self.assertFalse(result)

    @patch('requests.post')
    def test_refresh_token_failure_text(self, mock_post):
        """Test failed token refresh with text error response"""
        # Mock failed refresh response with text error
        mock_post.return_value = MagicMock(
            status_code=400,
            json=MagicMock(side_effect=ValueError),
            text='Invalid refresh token'
        )
        
        # Create API instance with expired token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'old_access_token'
        api.refresh_token = 'old_refresh_token'
        api.token_expires = datetime.now().timestamp() - 100
        
        # Test token refresh
        result = api._refresh_token()
        self.assertFalse(result)

    def test_cache_handling(self):
        """Test cache handling for tokens"""
        # Test cache loading
        self.assertIsNotNone(self.api.access_token)
        self.assertIsNotNone(self.api.refresh_token)
        
        # Test cache saving
        self.api.cache.save_tokens(
            'test_access_token',
            'test_refresh_token',
            time.time() + 3600
        )
        
        # Test cache loading again
        self.api.cache.load_tokens()
        self.assertEqual(self.api.access_token, 'test_access_token')
        self.assertEqual(self.api.refresh_token, 'test_refresh_token')

    def test_expired_token_handling(self):
        """Test handling of expired tokens"""
        # Create API instance with expired token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'expired_token'
        api.refresh_token = 'test_refresh_token'
        api.token_expires = datetime.now().timestamp() - 3600
        
        # Mock refresh response
        mock_response = MagicMock(
            status_code=200,
            json=lambda: {
                'access_token': 'new_access_token',
                'refresh_token': 'new_refresh_token',
                'expires_in': 3600
            }
        )
        
        with patch('requests.post', return_value=mock_response):
            # Test token refresh
            result = api._refresh_token()
            self.assertTrue(result)
            self.assertEqual(api.access_token, 'new_access_token')
            self.assertEqual(api.refresh_token, 'new_refresh_token')

    def test_api_functionality(self):
        """Test API functionality with valid tokens"""
        # Create API instance with valid tokens
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'valid_token'
        api.refresh_token = 'valid_refresh_token'
        api.token_expires = time.time() + 3600
        
        # Mock API response
        mock_response = MagicMock(
            status_code=200,
            json=lambda: {'data': []}
        )
        
        with patch('requests.get', return_value=mock_response):
            # Test API call
            result = api.get_anime_list()
            self.assertTrue(result)

    def test_error_handling(self):
        """Test error handling"""
        # Create API instance
        api = MyAnimeList('test_client_id', auto_authorize=False)
        
        # Mock error response
        mock_response = MagicMock(
            status_code=400,
            json=lambda: {'message': 'Bad request'}
        )
        
        with patch('requests.get', return_value=mock_response):
            # Test API call
            with self.assertRaises(Exception):
                api.get_anime_list()

    def test_rate_limiting(self):
        """Test rate limiting"""
        # Create API instance
        api = MyAnimeList('test_client_id', auto_authorize=False)
        
        # Mock rate limit response
        mock_response = MagicMock(
            status_code=429,
            headers={'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': str(time.time() + 10)}
        )
        
        with patch('requests.get', return_value=mock_response):
            # Test API call
            with self.assertRaises(Exception):
                api.get_anime_list()

    def test_token_validation(self):
        """Test token validation"""
        # Create API instance with invalid token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'invalid_token'
        
        # Mock error response
        mock_response = MagicMock(
            status_code=401,
            json=lambda: {'message': 'Unauthorized'}
        )
        
        with patch('requests.get', return_value=mock_response):
            # Test API call
            with self.assertRaises(Exception):
                api.get_anime_list()
        response2 = api._make_request('https://api.myanimelist.net/v2/users/@me/animelist')
        api.refresh_token = 'test_refresh_token'
        api.token_expires = datetime.now().timestamp() - 3600
        
        # Mock refresh response
        mock_response = MagicMock(
            status_code=200,
            json=lambda: {
                'access_token': 'new_access_token',
                'refresh_token': 'new_refresh_token',
                'expires_in': 3600
            }
        )
        
        with patch('requests.post', return_value=mock_response):
            # Test token refresh
            result = api._refresh_token()
            self.assertTrue(result)
            self.assertEqual(api.access_token, 'new_access_token')
            self.assertEqual(api.refresh_token, 'new_refresh_token')

    def test_token_expiration(self):
        """Test token expiration"""
        # Create API instance with expired token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'expired_token'
        api.refresh_token = 'test_refresh_token'
        api.token_expires = datetime.now().timestamp() - 3600
        
        # Test token expiration
        self.assertTrue(api._is_token_expired())

    def test_token_refresh_failure(self):
        """Test token refresh failure"""
        # Create API instance with expired token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'expired_token'
        api.refresh_token = 'test_refresh_token'
        api.token_expires = datetime.now().timestamp() - 3600
        
        # Mock failed refresh response
        mock_response = MagicMock(
            status_code=400,
            json=lambda: {'message': 'Invalid refresh token'}
        )
        
        with patch('requests.post', return_value=mock_response):
            # Test token refresh
            result = api._refresh_token()
            self.assertFalse(result)

    def test_token_refresh_failure_text(self):
        """Test token refresh failure with text error"""
        # Create API instance with expired token
        api = MyAnimeList('test_client_id', auto_authorize=False)
        api.access_token = 'expired_token'
        api.refresh_token = 'test_refresh_token'
        api.token_expires = datetime.now().timestamp() - 3600
        
        # Mock failed refresh response
        mock_response = MagicMock(
            status_code=400,
            json=MagicMock(side_effect=ValueError),
            text='Invalid refresh token'
        )
        
        with patch('requests.post', return_value=mock_response):
            # Test token refresh
            result = api._refresh_token()
            self.assertFalse(result)

    # Test cache loading
    def test_cache_loading(self):
        self.assertIsNotNone(self.api.access_token)
        self.assertIsNotNone(self.api.refresh_token)
        self.assertIsNotNone(self.api.token_expires)
        
    # Test cache saving
    def test_cache_saving(self):
        new_access_token = 'new_access_token'
        new_refresh_token = 'new_refresh_token'
        new_expires = datetime.now().timestamp() + 3600
        
        self.api.save_tokens(new_access_token, new_refresh_token, new_expires)
        
        # Verify cache was saved
        cached_tokens = self.cache.get('tokens.json')
        self.assertEqual(cached_tokens['access_token'], new_access_token)
        self.assertEqual(cached_tokens['refresh_token'], new_refresh_token)
        self.assertEqual(cached_tokens['expires_in'], new_expires)

if __name__ == '__main__':
    unittest.main()
