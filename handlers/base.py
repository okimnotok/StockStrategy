import http.server
import json
import queue
from multiprocessing import JoinableQueue
import time
from route import r


class SyncRoute:
    def __init__(self, f):
        self.f = f

    def __call__(self, o):
        length = int(o.headers.get('Content-Length', 0))
        path = o.path
        data = json.loads(o.rfile.read(length).devode()) if o.headers.get('Content-Type') == 'application/json' else o.rfile.read(length).decode()
        if path not in r.route_map.keys():
            raise NotImplemented
        status_code, message = r.route_map[path]['handler'].sync_handler(queue=o.batch_queue, path=path, data=data)
        return self.f(o, status_code, message)


def exception_handler(f):
    def wrapper(o):
        try:
            f(o)
        except Exception as e:
            o.send_response(e.code, e.message)
            o.send_header('Content-Type', 'text/plain; charset=utf-8')
            o.end_headers()
    return wrapper


class SyncServer(http.server.BaseHTTPRequestHandler):

    def __handle_response(self, status_code, data):
        self.send_response(status_code, data)
        if isinstance(data, dict):
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))

    @classmethod
    def set_queue(cls, batch_queue):
        cls.batch_queue = batch_queue

    @exception_handler
    @SyncRoute
    def do_POST(self, status_code, data):
        self.__handle_response(status_code, data)

    @exception_handler
    @SyncRoute
    def do_GET(self, status_code, data):
        self.__handle_response(status_code, data)

    @exception_handler
    @SyncRoute
    def do_DELETE(self, status_code, data):
        self.__handle_response(status_code, data)


class AsyncServer:
    def __init__(self, queue: JoinableQueue):
        self.queue = queue

    def _handler(self, handler, data):
        handler.async_handler(**data)

    def handler(self):
        while True:
            while not self.queue.empty():
                try:
                    pass
                except queue.Empty as e:
                    break
            time.sleep(1)


class BaseHandler:
    def sync_handler(self, queue, path, data, **kwargs):
        queue.put({
            'path': path,
            'data': data
        })
        return 202, 'accept request'

    def async_handler(self, **kwargs):
        pass

