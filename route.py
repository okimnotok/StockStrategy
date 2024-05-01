class Route:
    def __init__(self):
        self.route_map = {}

    def register(self, path, sync_class):
        self.route_map[path] = {
            'handler': sync_class()
        }


r = Route()
