class WatchlistManager:
    def __init__(self, sort_by=0, order=0, show_progress=True, reminder_enabled=True, limit=100, refresh_interval=60, group_by=0):
        self.sort_by = sort_by
        self.order = order
        self.show_progress = show_progress
        self.reminder_enabled = reminder_enabled
        self.limit = limit
        self.refresh_interval = refresh_interval
        self.group_by = group_by 