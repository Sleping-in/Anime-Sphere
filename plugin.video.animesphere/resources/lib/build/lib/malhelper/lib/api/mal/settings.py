import os
import logging

def get_setting(key, type='str', default=None):
    """Get a setting value from Kodi or environment"""
    try:
        # Try to get from environment first
        env_key = f'MAL_{key.upper()}'.replace('_', '_')
        if env_key in os.environ:
            value = os.environ[env_key]
            if type == 'int':
                return int(value) if value else 0
            return value
            
        # Try to get from Kodi addon
        import xbmcaddon
        addon = xbmcaddon.Addon()
        value = addon.getSetting(key)
        if type == 'int':
            return int(value) if value else 0
        return value
        
    except ImportError:
        # If running in test environment, return default
        return default
    except Exception as e:
        logging.error(f"Error getting setting {key}: {str(e)}")
        return default
