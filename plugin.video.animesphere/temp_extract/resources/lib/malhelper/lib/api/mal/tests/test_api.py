"""
Tests for the API functionality
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from ..api import MyAnimeList

class TestAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Mock requests module
        self.requests_mock = MagicMock()
        self.requests_mock.get.return_value = MagicMock(status_code=200, json=lambda: {})
        self.requests_mock.post.return_value = MagicMock(status_code=200, json=lambda: {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600,
            'token_type': 'Bearer'
        })
        
        # Patch requests module
        self.requests_patch = patch('malhelper.lib.api.mal.api.requests', self.requests_mock)
        self.requests_patch.start()
        
        # Initialize API
        self.api = MyAnimeList(
            client_id='test_client_id',
            client_secret='test_client_secret',
            auto_authorize=True
        )
        
        # Set token expiration
        self.api.token_expires = datetime.now().timestamp() + 3600

    def test_get_anime_details(self):
        """Test getting anime details"""
        mock_response = {
            'id': 1,
            'title': 'Test Anime',
            'main_picture': {'medium': 'url1', 'large': 'url2'},
            'alternative_titles': {'en': 'English Title'},
            'start_date': '2023-01-01',
            'end_date': '2023-03-01',
            'synopsis': 'Test synopsis',
            'mean': 8.5,
            'rank': 1,
            'popularity': 1,
            'num_list_users': 1000,
            'num_scoring_users': 500,
            'num_episodes': 12,
            'recommendations': [
                {
                    'node': {
                        'id': 2,
                        'title': 'Similar Anime 1',
                        'main_picture': {'medium': 'url3', 'large': 'url4'},
                        'recommendation_count': 100
                    }
                },
                {
                    'node': {
                        'id': 3,
                        'title': 'Similar Anime 2',
                        'main_picture': {'medium': 'url5', 'large': 'url6'},
                        'recommendation_count': 150
                    }
                }
            ]
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_anime_details(1)
            self.assertEqual(result['id'], 1)
            self.assertEqual(result['title'], 'Test Anime')
            self.assertEqual(result['num_episodes'], 12)
            self.assertEqual(len(result['recommendations']), 2)
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/1',
                params={'fields': 'recommendations'}
            )

    def test_get_anime_ranking(self):
        """Test getting anime ranking"""
        mock_response = {
            'data': [
                {
                    'node': {
                        'id': 1,
                        'title': 'Test Anime',
                        'mean': 8.5,
                        'rank': 1,
                        'popularity': 1,
                        'num_list_users': 1000,
                        'num_scoring_users': 500,
                        'nsfw': 'white',
                        'created_at': '2023-01-01',
                        'updated_at': '2023-01-01',
                        'media_type': 'tv',
                        'status': 'finished_airing',
                        'genres': [{'name': 'Action'}, {'name': 'Adventure'}],
                        'num_episodes': 12,
                        'start_date': '2023-01-01',
                        'end_date': '2023-03-01',
                        'synopsis': 'Test synopsis'
                    }
                }
            ],
            'paging': {
                'next': 'https://api.myanimelist.net/v2/anime/ranking?ranking_type=all&limit=100&offset=100'
            }
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_anime_ranking()
            self.assertEqual(len(result['data']), 1)
            self.assertEqual(result['data'][0]['node']['id'], 1)
            self.assertEqual(result['data'][0]['node']['title'], 'Test Anime')
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/ranking',
                params={'ranking_type': 'all', 'limit': 100}
            )

    def test_get_seasonal_anime(self):
        """Test getting seasonal anime"""
        mock_response = {
            'data': [
                {
                    'node': {
                        'id': 1,
                        'title': 'Test Anime',
                        'mean': 8.5,
                        'rank': 1,
                        'popularity': 1,
                        'num_list_users': 1000,
                        'num_scoring_users': 500,
                        'nsfw': 'white',
                        'created_at': '2023-01-01',
                        'updated_at': '2023-01-01',
                        'media_type': 'tv',
                        'status': 'finished_airing',
                        'genres': [{'name': 'Action'}, {'name': 'Adventure'}],
                        'num_episodes': 12,
                        'start_date': '2023-01-01',
                        'end_date': '2023-03-01',
                        'synopsis': 'Test synopsis'
                    }
                }
            ],
            'paging': {
                'next': 'https://api.myanimelist.net/v2/anime/season?year=2023&season=spring&limit=100&offset=100'
            }
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_seasonal_anime(year=2023, season='spring')
            self.assertEqual(len(result['data']), 1)
            self.assertEqual(result['data'][0]['node']['id'], 1)
            self.assertEqual(result['data'][0]['node']['title'], 'Test Anime')
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/season',
                params={'year': 2023, 'season': 'spring', 'limit': 100}
            )

    def test_get_mal_id(self):
        """Test getting MAL ID"""
        mock_response = MagicMock(
            status_code=200,
            json=lambda: {
                'data': [
                    {'node': {'id': 1, 'title': 'Test Anime'}}
                ]
            }
        )
        
        with patch('requests.request', return_value=mock_response) as mock_request:
            result = self.api.get_mal_id(title='Test Anime')
            self.assertEqual(result, 1)
            mock_request.assert_called_once()

    def test_add_to_watchlist(self):
        """Test adding anime to watchlist"""
        mock_response = {
            'status': 'plan_to_watch',
            'num_watched_episodes': 0
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.add_to_watchlist(1)
            self.assertEqual(result['status'], 'plan_to_watch')
            self.assertEqual(result['num_watched_episodes'], 0)
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/1/my_list_status',
                method='PUT',
                data={'status': 'plan_to_watch'}
            )

    def test_update_progress(self):
        """Test updating watched episode count"""
        mock_response = {
            'status': 'watching',
            'num_watched_episodes': 5
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.update_progress(1, 5)
            self.assertEqual(result['status'], 'watching')
            self.assertEqual(result['num_watched_episodes'], 5)
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/1/my_list_status',
                method='PUT',
                data={'num_watched_episodes': 5}
            )

    def test_get_watch_status(self):
        """Test getting watch status"""
        mock_response = {
            'my_list_status': {
                'status': 'watching',
                'num_watched_episodes': 5
            }
        }
    
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_watch_status(1)
            self.assertEqual(result['my_list_status']['status'], 'watching')
            self.assertEqual(result['my_list_status']['num_watched_episodes'], 5)
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/1',
                params={'fields': 'my_list_status'}
            )

    def test_get_episode_history(self):
        """Test getting episode viewing history"""
        mock_response = {
            'my_list_status': {
                'episode_history': [
                    {'episode': 1},
                    {'episode': 2}
                ]
            }
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_episode_history(1)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['episode'], 1)
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/1',
                params={'fields': 'my_list_status'}
            )

    def test_get_recently_watched(self):
        """Test getting recently watched anime"""
        mock_response = {
            'data': [
                {
                    'node': {
                        'id': 1,
                        'title': 'Anime 1',
                        'num_episodes': 12,
                        'my_list_status': {
                            'status': 'watching',
                            'num_episodes_watched': 1
                        }
                    }
                },
                {
                    'node': {
                        'id': 2,
                        'title': 'Anime 2',
                        'num_episodes': 24,
                        'my_list_status': {
                            'status': 'on_hold',
                            'num_episodes_watched': 5
                        }
                    }
                }
            ]
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_recently_watched()
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['node']['id'], 1)
            self.assertEqual(result[0]['node']['my_list_status']['num_episodes_watched'], 1)
            self.assertEqual(result[1]['node']['id'], 2)
            self.assertEqual(result[1]['node']['my_list_status']['num_episodes_watched'], 5)
            mock_request.assert_called_once()

    def test_get_next_episodes(self):
        """Test getting next episodes to watch"""
        mock_response = {
            'data': [
                {
                    'node': {
                        'id': 1,
                        'title': 'Anime 1',
                        'num_episodes': 12,
                        'my_list_status': {
                            'status': 'watching',
                            'num_episodes_watched': 1
                        }
                    }
                },
                {
                    'node': {
                        'id': 2,
                        'title': 'Anime 2',
                        'num_episodes': 24,
                        'my_list_status': {
                            'status': 'watching',
                            'num_episodes_watched': 2
                        }
                    }
                }
            ]
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_next_episodes()
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 1)
            self.assertEqual(result[0]['episode'], 2)
            self.assertEqual(result[1]['id'], 2)
            self.assertEqual(result[1]['episode'], 3)
            mock_request.assert_called_once()

    def test_get_studio_anime(self):
        """Test getting anime from a studio"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'node': {
                        'id': 1,
                        'title': 'Studio Anime 1',
                        'main_picture': {'medium': 'url1', 'large': 'url2'},
                        'alternative_titles': {'en': 'English Title'},
                        'start_date': '2023-01-01',
                        'end_date': '2023-03-01',
                        'synopsis': 'Test synopsis',
                        'mean': 8.5,
                        'rank': 1,
                        'popularity': 1,
                        'num_list_users': 1000,
                        'num_scoring_users': 500,
                        'num_episodes': 12
                    }
                },
                {
                    'node': {
                        'id': 2,
                        'title': 'Studio Anime 2',
                        'main_picture': {'medium': 'url3', 'large': 'url4'},
                        'alternative_titles': {'en': 'English Title 2'},
                        'start_date': '2023-04-01',
                        'end_date': '2023-06-01',
                        'synopsis': 'Test synopsis 2',
                        'mean': 9.0,
                        'rank': 2,
                        'popularity': 2,
                        'num_list_users': 1500,
                        'num_scoring_users': 700,
                        'num_episodes': 24
                    }
                }
            ]
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_studio_anime(1)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 1)
            self.assertEqual(result[1]['id'], 2)
            mock_request.assert_called_once()

    def test_get_episode_progress(self):
        """Test getting episode progress"""
        mock_response = {
            'my_list_status': {
                'num_watched_episodes': 2,
                'total_episodes': 12,
                'next_episode': 3,
                'episode_history': [
                    {'episode': 1},
                    {'episode': 2}
                ]
            }
        }
    
        with patch.object(self.api, '_make_request', return_value=mock_response) as mock_request:
            result = self.api.get_episode_progress(1)
            self.assertEqual(result['num_watched_episodes'], 2)
            self.assertEqual(result['total_episodes'], 12)
            self.assertEqual(result['next_episode'], 3)
            self.assertEqual(len(result['episode_history']), 2)
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/1',
                params={'fields': 'my_list_status'}
            )
            mock_request.assert_called_once_with(
                'https://api.myanimelist.net/v2/anime/1',
                params={'fields': 'my_list_status'}
            )

    def test_get_similar_anime(self):
        """Test getting similar anime"""
        mock_response = {
            'id': 1,
            'title': 'Test Anime',
            'recommendations': [
                {
                    'node': {
                        'id': 2,
                        'title': 'Similar Anime 1',
                        'main_picture': {'medium': 'url1', 'large': 'url2'},
                        'recommendation_count': 100
                    }
                },
                {
                    'node': {
                        'id': 3,
                        'title': 'Similar Anime 2',
                        'main_picture': {'medium': 'url3', 'large': 'url4'},
                        'recommendation_count': 150
                    }
                }
            ]
        }
        
        with patch.object(self.api, 'get_anime_details', return_value=mock_response) as mock_request:
            result = self.api.get_similar_anime(1)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 2)
            self.assertEqual(result[0]['title'], 'Similar Anime 1')
            self.assertEqual(result[0]['main_picture'], {'medium': 'url1', 'large': 'url2'})
            self.assertEqual(result[0]['recommendation_count'], 100)
            mock_request.assert_called_once()

    def test_get_studio_anime(self):
        """Test getting anime from a studio"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {
                    'node': {
                        'id': 1,
                        'title': 'Studio Anime 1',
                        'main_picture': {'medium': 'url1', 'large': 'url2'},
                        'alternative_titles': {'en': 'English Title'},
                        'start_date': '2023-01-01',
                        'end_date': '2023-03-01',
                        'synopsis': 'Test synopsis',
                        'mean': 8.5,
                        'rank': 1,
                        'popularity': 1,
                        'num_list_users': 1000,
                        'num_scoring_users': 500,
                        'num_episodes': 12
                    }
                },
                {
                    'node': {
                        'id': 2,
                        'title': 'Studio Anime 2',
                        'main_picture': {'medium': 'url3', 'large': 'url4'},
                        'alternative_titles': {'en': 'English Title 2'},
                        'start_date': '2023-04-01',
                        'end_date': '2023-06-01',
                        'synopsis': 'Test synopsis 2',
                        'mean': 9.0,
                        'rank': 2,
                        'popularity': 2,
                        'num_list_users': 1500,
                        'num_scoring_users': 700,
                        'num_episodes': 24
                    }
                }
            ]
        }
        
        with patch.object(self.api, '_make_request', return_value=mock_response.json.return_value) as mock_request:
            result = self.api.get_studio_anime(1)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['id'], 1)
            self.assertEqual(result[0]['title'], 'Studio Anime 1')
            self.assertEqual(result[0]['main_picture'], {'medium': 'url1', 'large': 'url2'})
            self.assertEqual(result[0]['num_episodes'], 12)
            mock_request.assert_called_once()

if __name__ == '__main__':
    unittest.main()
