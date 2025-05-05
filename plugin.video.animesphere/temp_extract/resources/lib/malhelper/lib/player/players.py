import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from jurialmunkey.parser import parse_paramstring
from malhelper.lib.api.mal.api import MyAnimeList
import subprocess
import time
import logging
from ..utils.errors import MALHelperError, PlayerError, handle_error

class Players:
    def __init__(self, **params):
        self.params = params
        self.addon = xbmcaddon.Addon()
        self.mal = MyAnimeList()
        self._validate_settings()

    def _validate_settings(self):
        """Validate player settings"""
        if not self.addon.getSetting('players'):
            raise PlayerError('No players configured')

    def get_available_players(self):
        """Get available players from settings"""
        players = self.addon.getSetting('players').split(',')
        return [p.strip() for p in players if p.strip()]

    def get_player_settings(self, player_id):
        """Get settings for a specific player"""
        prefix = f'player_{player_id}_'
        settings = {}
        for setting in self.addon.getSettings().keys():
            if setting.startswith(prefix):
                key = setting.replace(prefix, '')
                settings[key] = self.addon.getSetting(setting)
        return settings

    def get_stream_quality(self, quality_setting):
        """Get stream quality based on setting"""
        qualities = {
            '0': 'best',
            '1': 'high',
            '2': 'medium',
            '3': 'low'
        }
        return qualities.get(quality_setting, 'best')

    def get_protocol(self, protocol_setting):
        """Get protocol based on setting"""
        protocols = {
            '0': 'http',
            '1': 'https',
            '2': 'rtmp',
            '3': 'rtsp'
        }
        return protocols.get(protocol_setting, 'http')

    def play_with_player(self, player_id, mal_id):
        """Play with a specific player"""
        try:
            player_settings = self.get_player_settings(player_id)
            player_type = player_settings.get('type', 'default')
            
            if player_type == 'default':
                self.play_default(mal_id)
            elif player_type == 'external':
                self.play_external(player_settings, mal_id)
            elif player_type == 'stream':
                self.play_stream(player_settings, mal_id)
            elif player_type == 'custom':
                self.play_custom(player_settings, mal_id)
        except PlayerError as e:
            handle_error(e)
            raise

    def play_default(self, mal_id):
        """Play with default player"""
        try:
            anime = self.mal.get_anime_details(mal_id)
            next_episode = self.mal.get_next_episode(mal_id)
            
            if next_episode:
                url = self.get_stream_url(anime, next_episode)
                self.play_url(url)
            else:
                raise PlayerError('No next episode available')
        except Exception as e:
            handle_error(PlayerError(str(e)))
            raise

    def play_external(self, settings, mal_id):
        """Play with external player"""
        try:
            anime = self.mal.get_anime_details(mal_id)
            next_episode = self.mal.get_next_episode(mal_id)
            
            if next_episode:
                url = self.get_stream_url(anime, next_episode)
                player_path = settings.get('path', '')
                player_args = settings.get('args', '')
                wait_for_player = settings.get('wait', 'false') == 'true'
                
                if not player_path:
                    raise PlayerError('External player path not configured')
                
                try:
                    args = [player_path] + player_args.split()
                    process = subprocess.Popen(args + [url])
                    
                    if wait_for_player:
                        process.wait()
                except Exception as e:
                    raise PlayerError(f'Failed to launch external player: {str(e)}')
            else:
                raise PlayerError('No next episode available')
        except Exception as e:
            handle_error(PlayerError(str(e)))
            raise

    def play_stream(self, settings, mal_id):
        """Play with stream player"""
        try:
            anime = self.mal.get_anime_details(mal_id)
            next_episode = self.mal.get_next_episode(mal_id)
            
            if next_episode:
                url = self.get_stream_url(anime, next_episode)
                stream_type = settings.get('type', '0')
                quality = self.get_stream_quality(settings.get('quality', '0'))
                
                if settings.get('use_inputstream', 'false') == 'true':
                    self.play_with_inputstream(url, settings)
                else:
                    self.play_url(url)
            else:
                raise PlayerError('No next episode available')
        except Exception as e:
            handle_error(PlayerError(str(e)))
            raise

    def play_custom(self, settings, mal_id):
        """Play with custom player"""
        try:
            anime = self.mal.get_anime_details(mal_id)
            next_episode = self.mal.get_next_episode(mal_id)
            
            if next_episode:
                url = self.get_stream_url(anime, next_episode)
                player_path = settings.get('path', '')
                player_args = settings.get('args', '')
                protocol = self.get_protocol(settings.get('protocol', '0'))
                
                if not player_path:
                    raise PlayerError('Custom player path not configured')
                
                try:
                    args = [player_path] + player_args.split()
                    process = subprocess.Popen(args + [f"{protocol}://{url}"])
                    
                    if settings.get('wait', 'false') == 'true':
                        process.wait()
                except Exception as e:
                    raise PlayerError(f'Failed to launch custom player: {str(e)}')
            else:
                raise PlayerError('No next episode available')
        except Exception as e:
            handle_error(PlayerError(str(e)))
            raise

    def get_stream_url(self, anime, episode):
        """Get stream URL for an episode"""
        try:
            # Implement stream URL generation logic here
            return f"https://example.com/anime/{anime['id']}/episode/{episode}"
        except Exception as e:
            handle_error(PlayerError(f'Failed to get stream URL: {str(e)}'))
            raise

    def play_url(self, url):
        """Play URL with default player"""
        try:
            listitem = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
        except Exception as e:
            handle_error(PlayerError(f'Failed to play URL: {str(e)}'))
            raise

    def play_with_inputstream(self, url, settings):
        """Play with inputstream"""
        try:
            listitem = xbmcgui.ListItem(path=url)
            listitem.setProperty('inputstream', 'inputstream.adaptive')
            listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
            if settings.get('subtitle_url'):
                listitem.setSubtitles([settings.get('subtitle_url')])
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
        except Exception as e:
            handle_error(PlayerError(f'Failed to play with inputstream: {str(e)}'))
            raise

    def play(self, handle=None):
        """Play anime episode"""
        mal_id = self.params.get('mal_id')
        if not mal_id:
            xbmc.log('MAL Helper Error: No MAL ID provided', xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
                'MAL Helper',
                'No anime selected',
                xbmcgui.NOTIFICATION_ERROR
            )
            return

        players = self.get_available_players()
        if not players:
            xbmcgui.Dialog().notification(
                'MAL Helper',
                'No players configured',
                xbmcgui.NOTIFICATION_ERROR
            )
            return

        # If only one player is configured, use it directly
        if len(players) == 1:
            self.play_with_player(players[0], mal_id)
            return

        # Show player selection dialog
        player_names = [self.addon.getLocalizedString(int(p)) for p in players]
        index = xbmcgui.Dialog().select(
            self.addon.getLocalizedString(32000),  # 'Select Player'
            player_names
        )

        if index >= 0:
            self.play_with_player(players[index], mal_id)
