import http.server
import socket
from multiprocessing import JoinableQueue, Process
from route import r

from handlers.base import SyncServer, AsyncServer
from handlers.health_check import HealthCheck

PORT = 10086
batch_queue = JoinableQueue()

PATH_CLASS_MAP = [
    ('/health', HealthCheck)
]


def initialize_route():
    for path, handler in PATH_CLASS_MAP:
        r.register(path, handler)


class HTTPServerV6(http.server.HTTPServer):
    address_family = socket.AF_INET6


class HTTPServerV4(http.server.HTTPServer):
    address_family = socket.AF_INET


if __name__ == '__main__':
    initialize_route()
    server_address = ("127.0.0.1", PORT)
    SyncServer.set_queue(batch_queue)
    process = Process(target=AsyncServer(batch_queue).handler, daemon=True)
    process.start()
    httpd = HTTPServerV4(server_address, SyncServer)
    httpd.serve_forever()
