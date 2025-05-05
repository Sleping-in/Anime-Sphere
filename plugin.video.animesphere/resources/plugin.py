if __name__ == '__main__':
    import sys
    import xbmc
    import xbmcgui
    import xbmcplugin
    from malhelper.lib.items.router import Router
    
    # Initialize Kodi plugin
    handle = int(sys.argv[1])
    params = sys.argv[2][1:]
    
    # Set content type
    xbmcplugin.setContent(handle, 'videos')
    
    # Initialize router
    router = Router(handle, params)
    
    try:
        router.run()
    except Exception as e:
        xbmc.log(f'MAL Helper Error: {str(e)}', xbmc.LOGERROR)
        xbmcgui.Dialog().notification('MAL Helper', 'An error occurred', xbmcgui.NOTIFICATION_ERROR)
