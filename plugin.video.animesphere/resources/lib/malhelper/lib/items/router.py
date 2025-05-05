# Mock Kodi modules
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

from resources.tests.mock_xbmc import xbmc, xbmcgui, xbmcplugin
from jurialmunkey.parser import parse_paramstring, reconfigure_legacy_params
from malhelper.lib.api.mal.api import MyAnimeList
from malhelper.lib.widgets.widgets import Widgets

class Router:
    def __init__(self, handle, paramstring, client_id):
        # plugin:// params configuration
        self.handle = handle
        self.paramstring, *secondary_params = paramstring.split('&&')
        self.params = reconfigure_legacy_params(**parse_paramstring(self.paramstring))
        self.mal = MyAnimeList(client_id)
        self.widgets = Widgets(client_id)
        
        if not secondary_params:
            return
        from urllib.parse import unquote_plus
        self.params['paths'] = [unquote_plus(i) for i in secondary_params]

    def _add_directory_item(self, title, params, is_folder=True, info=None, art=None):
        """Add a directory item to Kodi"""
        url = f'plugin://{self.params.get("addon_id")}/?{params}'
        li = xbmcgui.ListItem(title)
        
        if info:
            li.setInfo('video', info)
        if art:
            li.setArt(art)
        
        return xbmcplugin.addDirectoryItem(
            handle=self.handle,
            url=url,
            listitem=li,
            isFolder=is_folder
        )

    def _add_video_item(self, title, params, info=None, art=None):
        """Add a video item to Kodi"""
        url = f'plugin://{self.params.get("addon_id")}/?{params}'
        li = xbmcgui.ListItem(title)
        
        if info:
            li.setInfo('video', info)
        if art:
            li.setArt(art)
        
        return xbmcplugin.addDirectoryItem(
            handle=self.handle,
            url=url,
            listitem=li,
            isFolder=False
        )

    def _end_directory(self, succeeded=True, update_listing=False, cache_to_disc=True):
        """End the directory listing"""
        xbmcplugin.endOfDirectory(
            handle=self.handle,
            succeeded=succeeded,
            updateListing=update_listing,
            cacheToDisc=cache_to_disc
        )

    def play_external(self):
        """Play an external video"""
        from malhelper.lib.player.players import Players
        if not self.params.get('mal_id'):
            self.params['mal_id'] = self.mal.get_mal_id(**self.params)
        Players(**self.params).play(handle=self.handle if self.handle != -1 else None)

    def context_related(self):
        """Show related content"""
        from malhelper.lib.script.method.context_menu import related_lists
        if not self.params.get('mal_id'):
            self.params['mal_id'] = self.mal.get_mal_id(**self.params)
        self.params['container_update'] = True
        related_lists(include_play=True, **self.params)

    def get_directory(self, items_only=False, build_items=True):
        """Get directory listing"""
        from malhelper.lib.items.routes import get_container
        container = get_container(self.params.get('info'))(self.handle, self.paramstring, **self.params)
        container.get_mal_id()  # TODO: Only get this as necessary
        return container.get_directory(items_only, build_items)

    def show_main_menu(self):
        """Show the main menu"""
        items = [
            {'title': 'Browse Anime', 'params': {'info': 'anime_list'}},
            {'title': 'My Watchlist', 'params': {'info': 'watchlist'}},
            {'title': 'Recently Watched', 'params': {'info': 'recently_watched'}},
            {'title': 'Next Episodes', 'params': {'info': 'next_episodes'}},
            {'title': 'Trending Anime', 'params': {'info': 'trending'}},
            {'title': 'Popular Anime', 'params': {'info': 'popular'}},
            {'title': 'Settings', 'params': {'info': 'settings'}}
        ]
        
        for item in items:
            self._add_directory_item(
                item['title'],
                item['params']
            )
        
        self._end_directory()

    def show_anime_list(self):
        """Show anime list"""
        anime_list = self.mal.get_anime_ranking()
        for anime in anime_list.get('data', []):
            self._add_directory_item(
                anime['node']['title'],
                {'info': 'anime_details', 'mal_id': anime['node']['id']},
                info={
                    'plot': anime['node'].get('synopsis'),
                    'year': try_int(anime['node'].get('start_date')[:4]),
                    'genre': ', '.join([g['name'] for g in anime['node'].get('genres', [])]),
                    'rating': anime['node'].get('mean'),
                    'mediatype': 'video'
                },
                art={
                    'poster': anime['node']['main_picture']['medium'],
                    'fanart': anime['node']['main_picture']['large']
                }
            )
        self._end_directory()

    def show_anime_details(self):
        """Show anime details"""
        anime = self.mal.get_anime_details(self.params['mal_id'])
        
        # Add video item
        self._add_video_item(
            anime['title'],
            {'info': 'play', 'mal_id': self.params['mal_id']},
            info={
                'plot': anime.get('synopsis'),
                'year': try_int(anime.get('start_date')[:4]),
                'genre': ', '.join([g['name'] for g in anime.get('genres', [])]),
                'rating': anime.get('mean'),
                'mediatype': 'video',
                'duration': anime.get('average_episode_duration')
            },
            art={
                'poster': anime['main_picture']['medium'],
                'fanart': anime['main_picture']['large'],
                'banner': anime.get('background')
            }
        )
        
        # Add related content
        for related in anime.get('related_anime', []):
            self._add_directory_item(
                related['node']['title'],
                {'info': 'anime_details', 'mal_id': related['node']['id']},
                info={
                    'plot': related['node'].get('synopsis'),
                    'year': try_int(related['node'].get('start_date')[:4]),
                    'genre': ', '.join([g['name'] for g in related['node'].get('genres', [])]),
                    'rating': related['node'].get('mean'),
                    'mediatype': 'video'
                },
                art={
                    'poster': related['node']['main_picture']['medium'],
                    'fanart': related['node']['main_picture']['large']
                }
            )
        
        self._end_directory()

    def show_watchlist(self):
        """Show watchlist"""
        watchlist = self.mal.get_user_anime_list()
        for anime in watchlist.get('data', []):
            self._add_directory_item(
                anime['node']['title'],
                {'info': 'anime_details', 'mal_id': anime['node']['id']},
                info={
                    'plot': anime['node'].get('synopsis'),
                    'year': try_int(anime['node'].get('start_date')[:4]),
                    'genre': ', '.join([g['name'] for g in anime['node'].get('genres', [])]),
                    'rating': anime['node'].get('mean'),
                    'mediatype': 'video',
                    'playcount': anime['my_list_status'].get('num_watched_episodes', 0)
                },
                art={
                    'poster': anime['node']['main_picture']['medium'],
                    'fanart': anime['node']['main_picture']['large']
                }
            )
        self._end_directory()

    def run(self):
        """Run the router"""
        try:
            if self.params.get('info') == 'play':
                return self.play_external()
            elif self.params.get('info') == 'related':
                return self.context_related()
            elif self.params.get('info') == 'anime_details':
                return self.show_anime_details()
            elif self.params.get('info') == 'anime_list':
                return self.show_anime_list()
            elif self.params.get('info') == 'watchlist':
                return self.show_watchlist()
            elif self.params.get('info') == 'recently_watched':
                return self.show_recently_watched()
            elif self.params.get('info') == 'next_episodes':
                return self.show_next_episodes()
            elif self.params.get('info') == 'trending':
                return self.show_trending()
            elif self.params.get('info') == 'popular':
                return self.show_popular()
            else:
                return self.show_main_menu()
        except Exception as e:
            xbmc.log(f'MAL Helper Error: {str(e)}', xbmc.LOGERROR)
            xbmcgui.Dialog().notification('MAL Helper', 'An error occurred', xbmcgui.NOTIFICATION_ERROR)
            self._end_directory()
