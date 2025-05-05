class DeveloperTools:
    def __init__(self, debug_mode=False, log_level=0, api_debug=False, performance_debug=False, show_sql=False, show_network=False):
        self.debug_mode = debug_mode
        self.log_level = log_level
        self.api_debug = api_debug
        self.performance_debug = performance_debug
        self.show_sql = show_sql
        self.show_network = show_network 