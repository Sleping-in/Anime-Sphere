import xbmc
import xbmcgui
import xbmcplugin
from jurialmunkey.parser import parse_paramstring, reconfigure_legacy_params
from malhelper.lib.api.mal.api import MyAnimeList
from malhelper.lib.widgets.widgets import Widgets

class Container:
    def __init__(self, handle, paramstring, **params):
        self.handle = handle
        self.paramstring = paramstring
        self.params = params
        self.mal = MyAnimeList()
        self.widgets = Widgets()

    def get_mal_id(self):
        """Get MAL ID from params"""
        if not self.params.get('mal_id'):
            self.params['mal_id'] = self.mal.get_mal_id(**self.params)
        return self.params['mal_id']

    def get_directory(self, items_only=False, build_items=True):
        """Get directory listing"""
        if build_items:
            self.build_items()
        if not items_only:
            self.end_directory()

    def build_items(self):
        """Build directory items"""
        pass

    def end_directory(self, succeeded=True, update_listing=False, cache_to_disc=True):
        """End the directory listing"""
        xbmcplugin.endOfDirectory(
            handle=self.handle,
            succeeded=succeeded,
            updateListing=update_listing,
            cacheToDisc=cache_to_disc
        )

class AnimeList(Container):
    def build_items(self):
        """Build anime list items"""
        anime_list = self.mal.get_anime_ranking()
        for anime in anime_list.get('data', []):
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=f'plugin://{self.params.get("addon_id")}/?info=anime_details&mal_id={anime["node"]["id"]}',
                listitem=xbmcgui.ListItem(
                    anime['node']['title'],
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
                ),
                isFolder=True
            )

class Watchlist(Container):
    def build_items(self):
        """Build watchlist items"""
        watchlist = self.mal.get_user_anime_list()
        for anime in watchlist.get('data', []):
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=f'plugin://{self.params.get("addon_id")}/?info=anime_details&mal_id={anime["node"]["id"]}',
                listitem=xbmcgui.ListItem(
                    anime['node']['title'],
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
                ),
                isFolder=True
            )

class RecentlyWatched(Container):
    def build_items(self):
        """Build recently watched items"""
        recently_watched = self.widgets.get_widget_data('recently_watched')
        for anime in recently_watched:
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=f'plugin://{self.params.get("addon_id")}/?info=anime_details&mal_id={anime["mal_id"]}',
                listitem=xbmcgui.ListItem(
                    anime['title'],
                    info={
                        'plot': anime.get('synopsis'),
                        'year': try_int(anime.get('start_date')[:4]),
                        'genre': ', '.join([g['name'] for g in anime.get('genres', [])]),
                        'rating': anime.get('mean'),
                        'mediatype': 'video',
                        'playcount': anime.get('watched_episodes', 0)
                    },
                    art={
                        'poster': anime['thumbnail'],
                        'fanart': anime.get('fanart')
                    }
                ),
                isFolder=True
            )

class NextEpisodes(Container):
    def build_items(self):
        """Build next episodes items"""
        next_episodes = self.widgets.get_widget_data('next_episodes')
        for anime in next_episodes:
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=f'plugin://{self.params.get("addon_id")}/?info=anime_details&mal_id={anime["mal_id"]}',
                listitem=xbmcgui.ListItem(
                    f"{anime['title']} - Next Episode {anime['next_episode']}",
                    info={
                        'plot': anime.get('synopsis'),
                        'year': try_int(anime.get('start_date')[:4]),
                        'genre': ', '.join([g['name'] for g in anime.get('genres', [])]),
                        'rating': anime.get('mean'),
                        'mediatype': 'video',
                        'playcount': anime.get('watched_episodes', 0)
                    },
                    art={
                        'poster': anime['thumbnail'],
                        'fanart': anime.get('fanart')
                    }
                ),
                isFolder=True
            )

class Trending(Container):
    def build_items(self):
        """Build trending items"""
        trending = self.widgets.get_widget_data('trending')
        for anime in trending:
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=f'plugin://{self.params.get("addon_id")}/?info=anime_details&mal_id={anime["mal_id"]}',
                listitem=xbmcgui.ListItem(
                    anime['title'],
                    info={
                        'plot': anime.get('synopsis'),
                        'year': try_int(anime.get('start_date')[:4]),
                        'genre': ', '.join([g['name'] for g in anime.get('genres', [])]),
                        'rating': anime.get('mean'),
                        'mediatype': 'video'
                    },
                    art={
                        'poster': anime['thumbnail'],
                        'fanart': anime.get('fanart')
                    }
                ),
                isFolder=True
            )

class Popular(Container):
    def build_items(self):
        """Build popular items"""
        popular = self.widgets.get_widget_data('popular')
        for anime in popular:
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=f'plugin://{self.params.get("addon_id")}/?info=anime_details&mal_id={anime["mal_id"]}',
                listitem=xbmcgui.ListItem(
                    anime['title'],
                    info={
                        'plot': anime.get('synopsis'),
                        'year': try_int(anime.get('start_date')[:4]),
                        'genre': ', '.join([g['name'] for g in anime.get('genres', [])]),
                        'rating': anime.get('mean'),
                        'mediatype': 'video'
                    },
                    art={
                        'poster': anime['thumbnail'],
                        'fanart': anime.get('fanart')
                    }
                ),
                isFolder=True
            )

def get_container(info):
    """Get container class for info"""
    containers = {
        'anime_list': AnimeList,
        'watchlist': Watchlist,
        'recently_watched': RecentlyWatched,
        'next_episodes': NextEpisodes,
        'trending': Trending,
        'popular': Popular
    }
    return containers.get(info, Container)
