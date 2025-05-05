import requests
import json
import webbrowser
from urllib.parse import urlencode
import time
import os
import logging

def get_setting(key, type='str', default=None):
    """Get setting value"""
    settings = {
        'mal_client_id': 'd9abb9cbc9871ea3d55f1eb605f3e166',
        'mal_client_secret': '5179742b310a90862424cedf9e969c3de5ece34638962b2500ea98b3ef1afd0c',
        'mal_access_token': 'test_access_token',
        'api_timeout': 30
    }
    return settings.get(key, default)

def get_access_token(client_id, client_secret, username, password):
    """
    Get an access token from MyAnimeList using OAuth2
    
    Args:
        client_id (str): Your MyAnimeList API client ID
        client_secret (str): Your MyAnimeList API client secret
        username (str): Your MyAnimeList username
        password (str): Your MyAnimeList password
        
    Returns:
        dict: Access token information including access_token, refresh_token, and expires_in
    """
    # OAuth2 endpoints
    token_url = "https://api.myanimelist.net/v2/auth/token"
    
    # Prepare the request data
    token_data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        print("\nAttempting to get access token...")
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_info = response.json()
        
        # Save token information to file
        tokens_file = os.path.join(os.path.dirname(__file__), 'tokens.json')
        with open(tokens_file, 'w') as f:
            json.dump(token_info, f, indent=4)
        
        print("\nSuccessfully obtained access token!")
        print(f"Access token: {token_info['access_token']}")
        print(f"Refresh token: {token_info['refresh_token']}")
        print(f"Expires in: {token_info['expires_in']} seconds")
        print(f"\nToken information has been saved to: {tokens_file}")
        return token_info
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {str(e)}")
        if response.text:
            print(f"Server response: {response.text}")
        return None
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_info = response.json()
        
        # Save token information to file
        tokens_file = os.path.join(os.path.dirname(__file__), 'tokens.json')
        with open(tokens_file, 'w') as f:
            json.dump(token_info, f, indent=4)
        
        print("\nSuccessfully obtained access token!")
        print(f"Access token: {token_info['access_token']}")
        print(f"Refresh token: {token_info['refresh_token']}")
        print(f"Expires in: {token_info['expires_in']} seconds")
        print(f"\nToken information has been saved to: {tokens_file}")
        return token_info
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {str(e)}")
        return None

def refresh_access_token(client_id, refresh_token):
    """
    Refresh an expired access token
    
    Args:
        client_id (str): Your MyAnimeList API client ID
        refresh_token (str): The refresh token from previous authentication
        
    Returns:
        dict: New access token information
    """
    token_url = "https://myanimelist.net/v1/oauth2/token"
    
    token_data = {
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_info = response.json()
        
        # Save new token information
        tokens_file = os.path.join(os.path.dirname(__file__), 'tokens.json')
        with open(tokens_file, 'w') as f:
            json.dump(token_info, f, indent=4)
        
        print("\nSuccessfully refreshed access token!")
        print(f"New access token: {token_info['access_token']}")
        print(f"Expires in: {token_info['expires_in']} seconds")
        print(f"\nToken information has been saved to: {tokens_file}")
        return token_info
        
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing access token: {str(e)}")
        return None

def main():
    # Get client ID and secret from settings
    client_id = get_setting('mal_client_id', 'str')
    client_secret = get_setting('mal_client_secret', 'str')
    if not client_id or not client_secret:
        print("Error: Missing client ID or client secret. Please set them in your settings.")
        return
    
    # Use your credentials
    username = "E_Senshi"
    password = "Moh55378076"
    
    # Get new access token
    print("Getting new access token...")
    get_access_token(client_id, client_secret, username, password)

if __name__ == '__main__':
    main()
