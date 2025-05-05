#!/usr/bin/python3
import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import urllib.parse
from resources.lib.features.watchlist.manager import WatchlistManager
from resources.lib.features.sync.syncer import Syncer
from resources.lib.features.recommendations.recommender import Recommender
from resources.lib.features.notifications.notifier import Notifier
from resources.lib.features.performance.optimizer import Optimizer
from resources.lib.features.developer.tools import DeveloperTools

class AnimeSphere:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.base_url = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.args = urllib.parse.parse_qs(sys.argv[2][1:])
        self._load_settings()
        self._setup_features()

    def _load_settings(self):
        """Load all addon settings"""
        # API Settings
        self.mal_client_id = self.addon.getSetting('mal_client_id')
        self.mal_access_token = self.addon.getSetting('mal_access_token')
        self.api_debug = self.addon.getSetting('api_debug') == 'true'
        self.api_timeout = int(self.addon.getSetting('api_timeout'))
        self.api_retries = int(self.addon.getSetting('api_retries'))

        # Watchlist Settings
        self.watchlist_sort = int(self.addon.getSetting('watchlist_sort'))
        self.watchlist_order = int(self.addon.getSetting('watchlist_order'))
        self.show_progress = self.addon.getSetting('show_progress') == 'true'
        self.reminder_enabled = self.addon.getSetting('reminder_enabled') == 'true'
        self.watchlist_limit = int(self.addon.getSetting('watchlist_limit'))
        self.watchlist_refresh = int(self.addon.getSetting('watchlist_refresh'))
        self.watchlist_group_by = int(self.addon.getSetting('watchlist_group_by'))

        # Sync Settings
        self.sync_trakt = self.addon.getSetting('sync_trakt') == 'true'
        self.sync_anilist = self.addon.getSetting('sync_anilist') == 'true'
        self.sync_kitsu = self.addon.getSetting('sync_kitsu') == 'true'
        self.sync_shikimori = self.addon.getSetting('sync_shikimori') == 'true'
        self.sync_anidb = self.addon.getSetting('sync_anidb') == 'true'
        self.sync_interval = int(self.addon.getSetting('sync_interval'))
        self.sync_priority = int(self.addon.getSetting('sync_priority'))
        self.sync_conflict = int(self.addon.getSetting('sync_conflict'))

        # Recommendation Settings
        self.recommendation_type = int(self.addon.getSetting('recommendation_type'))
        self.max_recommendations = int(self.addon.getSetting('max_recommendations'))
        self.include_genres = self.addon.getSetting('include_genres')
        self.exclude_genres = self.addon.getSetting('exclude_genres')
        self.min_score = float(self.addon.getSetting('min_score'))
        self.max_age = int(self.addon.getSetting('max_age'))
        self.recommendation_refresh = int(self.addon.getSetting('recommendation_refresh'))

        # Notification Settings
        self.notify_new_episodes = self.addon.getSetting('notify_new_episodes') == 'true'
        self.notify_watchlist_updates = self.addon.getSetting('notify_watchlist_updates') == 'true'
        self.notify_recommendations = self.addon.getSetting('notify_recommendations') == 'true'
        self.notify_reminders = self.addon.getSetting('notify_reminders') == 'true'
        self.notification_duration = int(self.addon.getSetting('notification_duration'))
        self.notification_sound = self.addon.getSetting('notification_sound') == 'true'
        self.notification_sound_path = self.addon.getSetting('notification_sound_path')
        self.notification_position = int(self.addon.getSetting('notification_position'))
        self.notification_style = int(self.addon.getSetting('notification_style'))

        # Performance Settings
        self.cache_enabled = self.addon.getSetting('cache_enabled') == 'true'
        self.cache_ttl = int(self.addon.getSetting('cache_ttl'))
        self.background_refresh = self.addon.getSetting('background_refresh') == 'true'
        self.refresh_interval = int(self.addon.getSetting('refresh_interval'))
        self.thread_pool_size = int(self.addon.getSetting('thread_pool_size'))
        self.memory_limit = int(self.addon.getSetting('memory_limit'))
        self.cpu_priority = int(self.addon.getSetting('cpu_priority'))

        # Developer Settings
        self.debug_mode = self.addon.getSetting('debug_mode') == 'true'
        self.log_level = int(self.addon.getSetting('log_level'))
        self.api_debug = self.addon.getSetting('api_debug') == 'true'
        self.performance_debug = self.addon.getSetting('performance_debug') == 'true'
        self.show_sql = self.addon.getSetting('show_sql') == 'true'
        self.show_network = self.addon.getSetting('show_network') == 'true'

        # Player Settings
        self.players = self.addon.getSetting('players')
        self.default_player = int(self.addon.getSetting('default_player'))
        self.external_player_path = self.addon.getSetting('external_player_path')
        self.external_player_args = self.addon.getSetting('external_player_args')
        self.stream_quality = int(self.addon.getSetting('stream_quality'))
        self.stream_protocol = int(self.addon.getSetting('stream_protocol'))
        self.buffer_size = int(self.addon.getSetting('buffer_size'))
        self.subtitle_language = int(self.addon.getSetting('subtitle_language'))

        # Theme Settings
        self.theme = int(self.addon.getSetting('theme'))
        self.font_size = int(self.addon.getSetting('font_size'))
        self.icon_set = int(self.addon.getSetting('icon_set'))
        self.background_image = self.addon.getSetting('background_image')
        self.background_opacity = int(self.addon.getSetting('background_opacity'))

        # Widget Settings
        self.widget_enabled = self.addon.getSetting('widget_enabled') == 'true'
        self.widget_type = int(self.addon.getSetting('widget_type'))
        self.widget_limit = int(self.addon.getSetting('widget_limit'))
        self.widget_refresh = int(self.addon.getSetting('widget_refresh'))
        self.widget_style = int(self.addon.getSetting('widget_style'))

        # Backup Settings
        self.backup_enabled = self.addon.getSetting('backup_enabled') == 'true'
        self.backup_frequency = int(self.addon.getSetting('backup_frequency'))
        self.backup_location = self.addon.getSetting('backup_location')
        self.backup_retention = int(self.addon.getSetting('backup_retention'))
        self.backup_encryption = self.addon.getSetting('backup_encryption') == 'true'

        # Analytics Settings
        self.analytics_enabled = self.addon.getSetting('analytics_enabled') == 'true'
        self.analytics_type = int(self.addon.getSetting('analytics_type'))
        self.analytics_interval = int(self.addon.getSetting('analytics_interval'))
        self.analytics_anonymize = self.addon.getSetting('analytics_anonymize') == 'true'

        # Accessibility Settings
        self.screen_reader = self.addon.getSetting('screen_reader') == 'true'
        self.keyboard_navigation = self.addon.getSetting('keyboard_navigation') == 'true'
        self.high_contrast = self.addon.getSetting('high_contrast') == 'true'
        self.text_to_speech = self.addon.getSetting('text_to_speech') == 'true'
        self.closed_captions = self.addon.getSetting('closed_captions') == 'true'

    def _setup_features(self):
        """Initialize all features with proper configuration"""
        self.watchlist = WatchlistManager(
            sort_by=self.watchlist_sort,
            order=self.watchlist_order,
            show_progress=self.show_progress,
            reminder_enabled=self.reminder_enabled,
            limit=self.watchlist_limit,
            refresh_interval=self.watchlist_refresh,
            group_by=self.watchlist_group_by
        )

        self.sync = Syncer(
            sync_trakt=self.sync_trakt,
            sync_anilist=self.sync_anilist,
            sync_kitsu=self.sync_kitsu,
            sync_shikimori=self.sync_shikimori,
            sync_anidb=self.sync_anidb,
            sync_interval=self.sync_interval,
            sync_priority=self.sync_priority,
            sync_conflict=self.sync_conflict
        )

        self.recommender = Recommender(
            recommendation_type=self.recommendation_type,
            max_recommendations=self.max_recommendations,
            include_genres=self.include_genres,
            exclude_genres=self.exclude_genres,
            min_score=self.min_score,
            max_age=self.max_age,
            refresh_interval=self.recommendation_refresh
        )

        self.notifier = Notifier(
            notify_new_episodes=self.notify_new_episodes,
            notify_watchlist_updates=self.notify_watchlist_updates,
            notify_recommendations=self.notify_recommendations,
            notify_reminders=self.notify_reminders,
            notification_duration=self.notification_duration,
            notification_sound=self.notification_sound,
            notification_sound_path=self.notification_sound_path,
            notification_position=self.notification_position,
            notification_style=self.notification_style
        )

        self.optimizer = Optimizer(
            cache_enabled=self.cache_enabled,
            cache_ttl=self.cache_ttl,
            background_refresh=self.background_refresh,
            refresh_interval=self.refresh_interval,
            thread_pool_size=self.thread_pool_size,
            memory_limit=self.memory_limit,
            cpu_priority=self.cpu_priority
        )

        self.developer = DeveloperTools(
            debug_mode=self.debug_mode,
            log_level=self.log_level,
            api_debug=self.api_debug,
            performance_debug=self.performance_debug,
            show_sql=self.show_sql,
            show_network=self.show_network
        )

    def router(self, paramstring):
        """Route the request to the appropriate handler"""
        params = dict(urllib.parse.parse_qsl(paramstring))
        action = params.get('action', 'main_menu')

        if action == 'main_menu':
            self.show_main_menu()
        elif action == 'watchlist':
            self.show_watchlist()
        elif action == 'recommendations':
            self.show_recommendations()
        elif action == 'settings':
            self.show_settings()
        elif action == 'debug':
            self.show_debug_menu()
        elif action == 'play':
            self.play_item(params.get('mal_id'))
        else:
            self.show_main_menu()

    def show_main_menu(self):
        """Show the main menu with all available options"""
        items = [
            {
                'label': self.addon.getLocalizedString(32001),
                'url': f'{self.base_url}?action=watchlist',
                'is_folder': True
            },
            {
                'label': self.addon.getLocalizedString(32002),
                'url': f'{self.base_url}?action=recommendations',
                'is_folder': True
            },
            {
                'label': self.addon.getLocalizedString(32003),
                'url': f'{self.base_url}?action=settings',
                'is_folder': True
            },
            {
                'label': self.addon.getLocalizedString(32004),
                'url': f'{self.base_url}?action=debug',
                'is_folder': True
            }
        ]

        for item in items:
            list_item = xbmcgui.ListItem(label=item['label'])
            list_item.setArt({'thumb': 'resources/media/' + item['label'].lower().replace(' ', '_') + '.png'})
            list_item.setInfo('video', {
                'title': item['label'],
                'plot': self.addon.getLocalizedString(32005 + items.index(item))
            })
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=item['url'],
                listitem=list_item,
                isFolder=item['is_folder']
            )

        xbmcplugin.endOfDirectory(self.handle)

    def show_watchlist(self):
        """Show watchlist with all configured options"""
        watchlist = self.watchlist.get_watchlist()
        
        # Group items if configured
        if self.watchlist_group_by:
            groups = self.watchlist.group_by(self.watchlist_group_by)
            for group_name, items in groups.items():
                self._add_watchlist_group(group_name, items)
        else:
            for anime in watchlist:
                self._add_watchlist_item(anime)

        xbmcplugin.endOfDirectory(self.handle)

    def _add_watchlist_group(self, group_name, items):
        """Add a group of watchlist items"""
        group_item = xbmcgui.ListItem(label=group_name)
        group_item.setArt({'thumb': 'resources/media/group.png'})
        group_item.setInfo('video', {
            'title': group_name,
            'plot': f'{len(items)} items in this group'
        })
        group_url = f'{self.base_url}?action=watchlist_group&group={group_name}'
        xbmcplugin.addDirectoryItem(
            handle=self.handle,
            url=group_url,
            listitem=group_item,
            isFolder=True
        )

    def _add_watchlist_item(self, anime):
        """Add a single watchlist item"""
        list_item = xbmcgui.ListItem(label=anime['title'])
        list_item.setArt({
            'thumb': anime['main_picture']['medium'],
            'poster': anime['main_picture']['large'],
            'fanart': anime['main_picture']['large']
        })
        list_item.setInfo('video', {
            'title': anime['title'],
            'plot': anime['synopsis'],
            'rating': anime['mean'],
            'episode': anime['list_status']['num_watched_episodes'],
            'total_episodes': anime['num_episodes'],
            'year': anime['start_date'].split('-')[0] if anime.get('start_date') else None,
            'genre': ', '.join(anime.get('genres', []))
        })
        
        # Add context menu items
        context_items = [
            (self.addon.getLocalizedString(32006), f'RunPlugin({self.base_url}?action=play&mal_id={anime['id']})'),
            (self.addon.getLocalizedString(32007), f'RunPlugin({self.base_url}?action=remove_from_watchlist&mal_id={anime['id']})'),
            (self.addon.getLocalizedString(32008), f'RunPlugin({self.base_url}?action=mark_as_watched&mal_id={anime['id']})'),
            (self.addon.getLocalizedString(32009), f'RunPlugin({self.base_url}?action=mark_as_unwatched&mal_id={anime['id']})')
        ]
        list_item.addContextMenuItems(context_items)

        xbmcplugin.addDirectoryItem(
            handle=self.handle,
            url=f'{self.base_url}?action=play&mal_id={anime['id']}',
            listitem=list_item,
            isFolder=False
        )

    def show_recommendations(self):
        """Show recommendations with all configured options"""
        recommendations = self.recommender.get_recommendations(
            recommendation_type=self.recommendation_type,
            max_recommendations=self.max_recommendations,
            include_genres=self.include_genres,
            exclude_genres=self.exclude_genres,
            min_score=self.min_score,
            max_age=self.max_age
        )

        for anime in recommendations:
            list_item = xbmcgui.ListItem(label=anime['title'])
            list_item.setArt({
                'thumb': anime['main_picture']['medium'],
                'poster': anime['main_picture']['large'],
                'fanart': anime['main_picture']['large']
            })
            list_item.setInfo('video', {
                'title': anime['title'],
                'plot': anime['synopsis'],
                'rating': anime['mean'],
                'year': anime['start_date'].split('-')[0] if anime.get('start_date') else None,
                'genre': ', '.join(anime.get('genres', []))
            })

            # Add context menu items
            context_items = [
                (self.addon.getLocalizedString(32010), f'RunPlugin({self.base_url}?action=add_to_watchlist&mal_id={anime['id']})'),
                (self.addon.getLocalizedString(32011), f'RunPlugin({self.base_url}?action=mark_as_watched&mal_id={anime['id']})'),
                (self.addon.getLocalizedString(32012), f'RunPlugin({self.base_url}?action=mark_as_unwatched&mal_id={anime['id']})')
            ]
            list_item.addContextMenuItems(context_items)

            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=f'{self.base_url}?action=play&mal_id={anime['id']}',
                listitem=list_item,
                isFolder=False
            )

        xbmcplugin.endOfDirectory(self.handle)

    def show_settings(self):
        """Show settings menu with all categories"""
        self.addon.openSettings()

    def show_debug_menu(self):
        """Show debug menu with all options"""
        items = [
            {
                'label': self.addon.getLocalizedString(32013),
                'url': f'{self.base_url}?action=clear_cache',
                'is_folder': False
            },
            {
                'label': self.addon.getLocalizedString(32014),
                'url': f'{self.base_url}?action=show_logs',
                'is_folder': False
            },
            {
                'label': self.addon.getLocalizedString(32015),
                'url': f'{self.base_url}?action=show_api_debug',
                'is_folder': False
            },
            {
                'label': self.addon.getLocalizedString(32016),
                'url': f'{self.base_url}?action=show_performance_debug',
                'is_folder': False
            }
        ]

        for item in items:
            list_item = xbmcgui.ListItem(label=item['label'])
            xbmcplugin.addDirectoryItem(
                handle=self.handle,
                url=item['url'],
                listitem=list_item,
                isFolder=item['is_folder']
            )

        xbmcplugin.endOfDirectory(self.handle)

    def play_item(self, mal_id):
        """Play an anime item with configured player settings"""
        try:
            anime = self.watchlist.get_anime_details(mal_id)
            stream_url = self._get_stream_url(anime)
            
            list_item = xbmcgui.ListItem(path=stream_url)
            list_item.setArt({
                'thumb': anime['main_picture']['medium'],
                'poster': anime['main_picture']['large'],
                'fanart': anime['main_picture']['large']
            })
            list_item.setInfo('video', {
                'title': anime['title'],
                'plot': anime['synopsis'],
                'rating': anime['mean'],
                'episode': anime['list_status']['num_watched_episodes'],
                'total_episodes': anime['num_episodes']
            })

            # Set subtitle if configured
            if self.subtitle_language:
                subtitle_url = self._get_subtitle_url(anime, self.subtitle_language)
                list_item.setSubtitles([subtitle_url])

            # Set player settings
            list_item.setProperty('Inputstream', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            list_item.setProperty('inputstream.adaptive.stream_headers', f'User-Agent={self._get_user_agent()}')

            xbmcplugin.setResolvedUrl(self.handle, True, list_item)

        except Exception as e:
            self.notifier.show_error(
                self.addon.getLocalizedString(32017),
                f'Error playing anime: {str(e)}',
                self.notification_duration
            )

    def _get_stream_url(self, anime):
        """Get the stream URL based on configured player settings"""
        if self.default_player == 0:  # Default player
            return anime['stream_url']
        elif self.default_player == 1:  # External player
            return f'{self.external_player_path} {self.external_player_args} {anime['stream_url']}'
        elif self.default_player == 2:  # Stream player
            return f'{self.stream_protocol}://{anime['stream_url']}?quality={self.stream_quality}'
        else:  # Custom player
            return f'{self.custom_player_path} {self.custom_player_args} {anime['stream_url']}'

    def _get_subtitle_url(self, anime, language):
        """Get subtitle URL based on configured language"""
        if language == 0:  # None
            return None
        elif language == 1:  # English
            return anime.get('subtitle_urls', {}).get('en')
        elif language == 2:  # Japanese
            return anime.get('subtitle_urls', {}).get('ja')
        else:  # Auto
            return anime.get('subtitle_urls', {}).get('auto')

    def _get_user_agent(self):
        """Get user agent string for streaming"""
        return f'AnimeSphere/{self.addon.getAddonInfo('version')} (Kodi/{xbmc.getInfoLabel('System.BuildVersion').split()[0]})'

if __name__ == '__main__':
    addon = AnimeSphere()
    addon.router(sys.argv[2][1:])
