"""
Tests for the settings module
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from ..settings import get_setting

class TestSettings(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Save original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test fixtures"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_get_setting_env_str(self):
        """Test getting string setting from environment"""
        os.environ['MAL_CLIENT_ID'] = 'test_id'
        result = get_setting('client_id')
        self.assertEqual(result, 'test_id')

    def test_get_setting_env_int(self):
        """Test getting integer setting from environment"""
        os.environ['MAL_CLIENT_ID'] = '123'
        result = get_setting('client_id', type='int')
        self.assertEqual(result, 123)

    def test_get_setting_env_empty(self):
        """Test getting empty setting from environment"""
        os.environ['MAL_CLIENT_ID'] = ''
        result = get_setting('client_id', default='default_id')
        self.assertEqual(result, 'default_id')

    def test_get_setting_env_invalid_int(self):
        """Test getting invalid integer setting from environment"""
        os.environ['MAL_CLIENT_ID'] = 'not_an_int'
        result = get_setting('client_id', type='int', default=123)
        self.assertEqual(result, 123)

    def test_get_setting_kodi(self):
        """Test getting setting from Kodi addon"""
        # Mock xbmcaddon import
        with patch.dict('sys.modules', {'xbmcaddon': MagicMock()}):
            mock_addon = MagicMock()
            mock_instance = MagicMock()
            mock_instance.getSetting.return_value = 'test_value'
            mock_addon.return_value = mock_instance
            
            with patch('xbmcaddon.Addon', mock_addon):
                result = get_setting('test_setting')
                self.assertEqual(result, 'test_value')
                mock_instance.getSetting.assert_called_once_with('test_setting')

    def test_get_setting_kodi_int(self):
        """Test getting integer setting from Kodi addon"""
        # Mock xbmcaddon import
        with patch.dict('sys.modules', {'xbmcaddon': MagicMock()}):
            mock_addon = MagicMock()
            mock_instance = MagicMock()
            mock_instance.getSetting.return_value = '456'
            mock_addon.return_value = mock_instance
            
            with patch('xbmcaddon.Addon', mock_addon):
                result = get_setting('test_setting', type='int')
                self.assertEqual(result, 456)

    def test_get_setting_kodi_empty(self):
        """Test getting empty setting from Kodi addon"""
        # Mock xbmcaddon import
        with patch.dict('sys.modules', {'xbmcaddon': MagicMock()}):
            mock_addon = MagicMock()
            mock_instance = MagicMock()
            mock_instance.getSetting.return_value = ''
            mock_addon.return_value = mock_instance
            
            with patch('xbmcaddon.Addon', mock_addon):
                result = get_setting('test_setting', default='default_value')
                self.assertEqual(result, 'default_value')

    def test_get_setting_kodi_import_error(self):
        """Test getting setting with Kodi import error"""
        # Mock xbmcaddon import to raise ImportError
        with patch.dict('sys.modules', {'xbmcaddon': None}):
            result = get_setting('test_setting', default='default_value')
            self.assertEqual(result, 'default_value')

    def test_get_setting_kodi_invalid_int(self):
        """Test getting invalid integer setting from Kodi addon"""
        # Mock xbmcaddon import
        with patch.dict('sys.modules', {'xbmcaddon': MagicMock()}):
            mock_addon = MagicMock()
            mock_instance = MagicMock()
            mock_instance.getSetting.return_value = 'not_an_int'
            mock_addon.return_value = mock_instance
            
            with patch('xbmcaddon.Addon', mock_addon):
                result = get_setting('test_setting', type='int', default=789)
                self.assertEqual(result, 789)

    def test_get_setting_error(self):
        """Test getting setting with general error"""
        # Mock xbmcaddon import
        with patch.dict('sys.modules', {'xbmcaddon': MagicMock()}):
            mock_addon = MagicMock()
            mock_addon.side_effect = Exception('Test error')
            
            with patch('xbmcaddon.Addon', mock_addon):
                with patch('logging.error') as mock_error:
                    result = get_setting('test_setting', default='default_value')
                    self.assertEqual(result, 'default_value')
                    mock_error.assert_called()

if __name__ == '__main__':
    unittest.main()
