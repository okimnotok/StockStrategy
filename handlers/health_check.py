from handlers.base import BaseHandler


class HealthCheck(BaseHandler):
    def sync_handler(self, queue, path, data, **kwargs):
        return 202, {'hello': 'world'}