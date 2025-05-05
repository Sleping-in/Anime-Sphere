import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock Kodi modules
xbmc = MagicMock()
xbmcgui = MagicMock()
xbmcplugin = MagicMock()

# Add mocks to sys.modules
sys.modules['xbmc'] = xbmc
sys.modules['xbmcgui'] = xbmcgui
sys.modules['xbmcplugin'] = xbmcplugin

# Mock jurialmunkey parser module
jurialmunkey = MagicMock()
parser = MagicMock()
parser.try_int = lambda x, fallback=0: int(x) if x else fallback
parser.parse_paramstring = lambda x: {}
parser.reconfigure_legacy_params = lambda **kwargs: kwargs
jurialmunkey.parser = parser
sys.modules['jurialmunkey'] = jurialmunkey
sys.modules['jurialmunkey.parser'] = parser

# Mock MyAnimeList module
mal_module = MagicMock()
mal = MagicMock()
mal.get_anime_ranking = MagicMock(return_value={'data': []})
mal.get_user_anime_list = MagicMock(return_value={'data': []})
mal.get_anime_details = MagicMock(return_value={
    'title': 'Test Anime',
    'synopsis': 'Test synopsis',
    'start_date': '2023',
    'genres': [{'name': 'Action'}],
    'mean': 8.5,
    'main_picture': {
        'medium': 'test_medium.jpg',
        'large': 'test_large.jpg'
    }
})
mal.get_mal_id = MagicMock(return_value=123)
mal_module.MyAnimeList = MagicMock(return_value=mal)
sys.modules['malhelper.lib.api.mal.api'] = mal_module

from resources.lib.malhelper.lib.items.router import Router

class TestPlugin(unittest.TestCase):
    def setUp(self):
        # Mock sys.argv to simulate plugin invocation
        sys.argv = [
            'plugin://plugin.video.animesphere/',
            '123',
            '?info=main_menu&addon_id=plugin.video.animesphere'
        ]
        
        # Initialize router with mocked sys.argv
        self.handle = int(sys.argv[1])
        self.paramstring = sys.argv[2][1:]  # Remove '?' from query string
        self.router = Router(self.handle, self.paramstring, client_id='test_client_id')
        
    @patch('xbmcplugin.addDirectoryItem')
    @patch('xbmcplugin.endOfDirectory')
    def test_show_main_menu(self, mock_end_directory, mock_add_directory_item):
        """Test showing the main menu"""
        # Clear mocks before each test
        mock_add_directory_item.reset_mock()
        mock_end_directory.reset_mock()
        
        self.router.show_main_menu()
        
        # Verify main menu items were added
        expected_items = [
            'Browse Anime',
            'My Watchlist',
            'Recently Watched',
            'Next Episodes',
            'Trending Anime',
            'Popular Anime',
            'Settings'
        ]
        
        # Verify each expected item was added
        for item in expected_items:
            mock_add_directory_item.assert_any_call(
                handle=self.handle,
                url=unittest.mock.ANY,
                listitem=unittest.mock.ANY,
                isFolder=True
            )
        
        # Verify directory was ended
        mock_end_directory.assert_called_once_with(
            handle=self.handle,
            succeeded=True,
            updateListing=False,
            cacheToDisc=True
        )

    @patch('xbmcgui.ListItem')
    @patch('xbmcplugin.addDirectoryItem')
    def test_add_directory_item(self, mock_add_directory_item, mock_list_item):
        """Test adding a directory item"""
        # Clear mocks before each test
        mock_list_item.reset_mock()
        mock_add_directory_item.reset_mock()
        
        title = 'Test Item'
        params = 'info=test'
        info = {'plot': 'Test plot'}
        art = {'poster': 'test.jpg'}
        
        result = self.router._add_directory_item(title, params, info=info, art=art)
        
        # Verify ListItem creation
        mock_list_item.assert_called_once_with(title)
        mock_list_item.return_value.setInfo.assert_called_once_with('video', info)
        mock_list_item.return_value.setArt.assert_called_once_with(art)
        
        # Verify directory item addition
        mock_add_directory_item.assert_called_once_with(
            handle=self.handle,
            url=unittest.mock.ANY,
            listitem=unittest.mock.ANY,
            isFolder=True
        )
        self.assertTrue(result)

    @patch('xbmcplugin.endOfDirectory')
    def test_end_directory(self, mock_end_directory):
        """Test ending the directory"""
        # Clear mocks before each test
        mock_end_directory.reset_mock()
        
        self.router._end_directory()
        
        # Verify directory was ended with correct parameters
        mock_end_directory.assert_called_once_with(
            handle=self.handle,
            succeeded=True,
            updateListing=False,
            cacheToDisc=True
        )

if __name__ == '__main__':
    unittest.main()
