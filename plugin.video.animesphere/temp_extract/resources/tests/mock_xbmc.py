from unittest.mock import MagicMock

# Mock Kodi modules
class MockXbmc:
    LOGERROR = 4
    
class MockXbmcGui:
    
    class Dialog:
        def notification(self, *args, **kwargs):
            pass
    
    class ListItem:
        def __init__(self, *args, **kwargs):
            pass
        
        def setInfo(self, *args, **kwargs):
            pass
        
        def setArt(self, *args, **kwargs):
            pass

# Create mock modules
xbmc = MockXbmc()
xbmcgui = MockXbmcGui()
xbmcplugin = MagicMock()
