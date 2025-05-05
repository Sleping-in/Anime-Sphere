class Recommender:
    def __init__(self, recommendation_type=0, max_recommendations=10, include_genres="", exclude_genres="", min_score=7.5, max_age=5, refresh_interval=24):
        self.recommendation_type = recommendation_type
        self.max_recommendations = max_recommendations
        self.include_genres = include_genres
        self.exclude_genres = exclude_genres
        self.min_score = min_score
        self.max_age = max_age
        self.refresh_interval = refresh_interval 