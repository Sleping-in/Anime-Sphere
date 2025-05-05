class Notifier:
    def __init__(self, notify_new_episodes=True, notify_watchlist_updates=True, notify_recommendations=True, notify_reminders=True, notification_duration=5, notification_sound=True, notification_sound_path="", notification_position=0, notification_style=0):
        self.notify_new_episodes = notify_new_episodes
        self.notify_watchlist_updates = notify_watchlist_updates
        self.notify_recommendations = notify_recommendations
        self.notify_reminders = notify_reminders
        self.notification_duration = notification_duration
        self.notification_sound = notification_sound
        self.notification_sound_path = notification_sound_path
        self.notification_position = notification_position
        self.notification_style = notification_style 