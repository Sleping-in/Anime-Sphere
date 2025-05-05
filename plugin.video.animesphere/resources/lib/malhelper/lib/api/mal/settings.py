import os
import logging

def get_setting(key, type='str', default=None):
    """Get a setting value from Kodi or environment"""
    try:
        # Try to get from environment first
        env_key = f'MAL_{key.upper()}'
        if env_key in os.environ:
            value = os.environ[env_key]
            if not value:
                return default
            if type == 'int':
                return int(value)
            return value
            
        # Try to get from Kodi addon
        import xbmcaddon
        addon = xbmcaddon.Addon()
        value = addon.getSetting(key)
        if not value:
            return default
        if type == 'int':
            return int(value)
        return value
        
    except ImportError:
        # If running in test environment, return default
        return default
    except ValueError:
        logging.error(f"Invalid value for setting {key}: {value}")
        return default
    except Exception as e:
        logging.error(f"Error getting setting {key}: {str(e)}")
        return default
