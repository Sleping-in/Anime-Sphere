import xbmcaddon
import xbmcgui
import requests
import json
import time

def setup_mal_credentials():
    """Setup MyAnimeList credentials"""
    addon = xbmcaddon.Addon()
    
    # Get client ID and secret from user
    client_id = xbmcgui.Dialog().input('Enter MyAnimeList Client ID')
    if not client_id:
        xbmcgui.Dialog().notification('Error', 'Client ID is required')
        return False
    
    client_secret = xbmcgui.Dialog().input('Enter MyAnimeList Client Secret')
    if not client_secret:
        xbmcgui.Dialog().notification('Error', 'Client Secret is required')
        return False
    
    # Get username and password from user
    username = xbmcgui.Dialog().input('Enter MyAnimeList Username')
    if not username:
        xbmcgui.Dialog().notification('Error', 'Username is required')
        return False
    
    password = xbmcgui.Dialog().input('Enter MyAnimeList Password', option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not password:
        xbmcgui.Dialog().notification('Error', 'Password is required')
        return False
    
    try:
        # Get access token
        url = "https://api.myanimelist.net/v2/auth/token"
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        # Save credentials
        addon.setSetting('mal_client_id', client_id)
        addon.setSetting('mal_client_secret', client_secret)
        addon.setSetting('mal_username', username)
        addon.setSetting('mal_password', password)
        addon.setSetting('mal_access_token', token_data['access_token'])
        addon.setSetting('mal_refresh_token', token_data['refresh_token'])
        addon.setSetting('mal_token_expires', str(int(time.time()) + token_data['expires_in']))
        
        xbmcgui.Dialog().notification('Success', 'MyAnimeList credentials set up successfully')
        return True
        
    except Exception as e:
        xbmcgui.Dialog().notification('Error', f'Failed to get access token: {str(e)}')
        return False

def main():
    """Main function"""
    if setup_mal_credentials():
        # Test API connection
        try:
            from .api import MyAnimeList
            mal = MyAnimeList()
            test_response = mal.get_anime_details(1)  # Test with Cowboy Bebop
            if test_response:
                xbmcgui.Dialog().notification('Success', 'API connection test successful')
            else:
                xbmcgui.Dialog().notification('Error', 'API connection test failed')
        except Exception as e:
            xbmcgui.Dialog().notification('Error', f'API test failed: {str(e)}')

if __name__ == '__main__':
    main()
