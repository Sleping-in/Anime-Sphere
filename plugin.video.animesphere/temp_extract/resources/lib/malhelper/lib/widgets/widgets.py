from malhelper.lib.api.mal.api import MyAnimeList
from jurialmunkey.parser import try_int

# Widget types
WIDGET_TYPES = {
    'recently_watched': 'Recently Watched',
    'next_episodes': 'Next Episodes',
    'trending': 'Trending',
    'popular': 'Popular',
    'similar': 'Similar Anime',
    'studio': 'Studio Anime'
}


class Widgets:
    def __init__(self, client_id):
        self.mal = MyAnimeList(client_id)

    def get_widget_data(self, widget_type, limit=10, mal_id=None):
        """Get data for different widget types"""
        if widget_type == 'recently_watched':
            return self.get_recently_watched(limit)
        elif widget_type == 'next_episodes':
            return self.get_next_episodes(limit)
        elif widget_type == 'trending':
            return self.get_trending(limit)
        elif widget_type == 'popular':
            return self.get_popular(limit)
        elif widget_type == 'similar':
            return self.get_similar_anime(mal_id, limit)
        elif widget_type == 'studio':
            return self.get_studio_anime(mal_id, limit)
        return []

    def get_recently_watched(self, limit=10):
        """Get recently watched anime"""
        data = self.mal.get_user_anime_list(status='watching', sort='list_score', limit=limit)
        return self._format_widget_data(data)

    def get_next_episodes(self, limit=10):
        """Get next episodes to watch"""
        watching = self.mal.get_user_anime_list(status='watching', limit=limit)
        next_episodes = [anime for anime in watching.get('data', []) 
                        if anime.get('my_list_status', {}).get('num_watched_episodes', 0) < anime.get('num_episodes', 0)]
        return self._format_widget_data(next_episodes)

    def get_trending(self, limit=10):
        """Get trending anime"""
        data = self.mal.get_anime_ranking(ranking_type='trending', limit=limit)
        return self._format_widget_data(data, include_progress=False)

    def get_popular(self, limit=10):
        """Get popular anime"""
        data = self.mal.get_anime_ranking(ranking_type='popular', limit=limit)
        return self._format_widget_data(data, include_progress=False)

    def get_similar_anime(self, mal_id, limit=10):
        """Get similar anime recommendations"""
        data = self.mal.get_similar_anime(mal_id, limit)
        return self._format_widget_data(data, include_progress=False)

    def get_studio_anime(self, mal_id, limit=10):
        """Get anime from a specific studio"""
        data = self.mal.get_studio_anime(mal_id, limit)
        return self._format_widget_data(data, include_progress=False)

    def get_popular(self, limit=10):
        """Get popular anime"""
        data = self.mal.get_anime_ranking(ranking_type='popular', limit=limit)
        return self._format_widget_data(data)

    def _format_widget_data(self, data, include_progress=True):
        """Format widget data for Kodi"""
        formatted = []
        for item in data.get('data', []):
            anime = item.get('node', {})
            status = item.get('my_list_status', {})
            
            progress = {}
            if include_progress:
                progress = self.mal.get_episode_progress(anime.get('id'))

            formatted.append({
                'mal_id': anime.get('id'),
                'title': anime.get('title'),
                'thumbnail': anime.get('main_picture', {}).get('medium'),
                'status': status.get('status'),
                'watched_episodes': status.get('num_watched_episodes', 0),
                'total_episodes': anime.get('num_episodes', 0),
                'score': status.get('score'),
                'mean': anime.get('mean'),
                'rank': anime.get('rank'),
                'popularity': anime.get('popularity'),
                'next_episode': progress.get('next_episode'),
                'history': progress.get('history')
            })
        return formatted
