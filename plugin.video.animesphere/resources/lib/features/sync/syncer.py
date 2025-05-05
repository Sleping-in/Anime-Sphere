class Syncer:
    def __init__(self, sync_trakt=False, sync_anilist=False, sync_kitsu=False, sync_shikimori=False, sync_anidb=False, sync_interval=60, sync_priority=0, sync_conflict=0):
        self.sync_trakt = sync_trakt
        self.sync_anilist = sync_anilist
        self.sync_kitsu = sync_kitsu
        self.sync_shikimori = sync_shikimori
        self.sync_anidb = sync_anidb
        self.sync_interval = sync_interval
        self.sync_priority = sync_priority
        self.sync_conflict = sync_conflict 