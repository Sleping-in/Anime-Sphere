"""Stub implementations for Kodi modules for testing outside of Kodi"""

class xbmc:
    LOGDEBUG = 0
    LOGINFO = 1
    LOGWARNING = 2
    LOGERROR = 3
    
    def log(msg, level=0):
        print(f"[KodiStub] {msg}")

class xbmcaddon:
    @staticmethod
    def Addon():
        class Addon:
            def getSetting(self, key):
                return os.environ.get(f'KODI_{key.upper()}')
            
            def setSetting(self, key, value):
                os.environ[f'KODI_{key.upper()}'] = value
        return Addon()

class xbmcgui:
    class Dialog:
        def ok(self, heading, line):
            print(f"[Dialog] {heading}: {line}")
            return True
        
        def notification(self, heading, message, icon='info', time=5000):
            print(f"[Notification] {heading}: {message}")

class xbmcplugin:
    @staticmethod
    def setContent(handle, content):
        print(f"[Plugin] Setting content to {content}")
    
    @staticmethod
    def addDirectoryItem(handle, url, listitem, isFolder):
        print(f"[Plugin] Adding directory item: {url}")
    
    @staticmethod
    def endOfDirectory(handle):
        print("[Plugin] End of directory")
