class Optimizer:
    def __init__(self, cache_enabled=True, cache_ttl=60, background_refresh=True, refresh_interval=60, thread_pool_size=4, memory_limit=512, cpu_priority=0):
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.background_refresh = background_refresh
        self.refresh_interval = refresh_interval
        self.thread_pool_size = thread_pool_size
        self.memory_limit = memory_limit
        self.cpu_priority = cpu_priority 