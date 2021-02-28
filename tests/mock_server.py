from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import socket
from threading import Thread
import requests
from сlasses.vk_api_classes import read_textfile


class MockServerRequestHandler(BaseHTTPRequestHandler):
    USER_GET = re.compile(r'users.get')
    COUNTRIES_GET = re.compile(r'database.getCountries')
    CITIES_GET = re.compile(r'database.getCities')
    SEARCH_USERS_GET = re.compile(r'users.search')
    SEARCH_USER_BABYCH = re.compile(r'babych')
    PHOTOS_GET = re.compile(r'photos.get')

    def do_GET(self):
        if re.search(self.USER_GET, self.path):
            self.send('responses\\users.get.json')

        elif re.search(self.COUNTRIES_GET, self.path):
            self.send('responses\\database.getCountries.json')

        elif re.search(self.CITIES_GET, self.path):
            self.send('responses\\database.getCities.json')

        elif re.search(self.SEARCH_USERS_GET, self.path):
            if re.search(self.SEARCH_USER_BABYCH, self.path):
                self.send('responses\\users.search_babych.json')
            else:
                self.send('responses\\users.search.json')

        elif re.search(self.PHOTOS_GET, self.path):
            self.send('responses\\photos.get.json')

        else:
            self.send(fail=True)

    def send_headers(self, fail: bool = False):
        if fail:
            self.send_error(404)
        else:
            self.send_response(requests.codes.ok)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

    def send(self, filename: str = '', fail: bool = False):
        if not fail:
            self.send_headers()
            self.wfile.write(read_textfile(filename).encode('utf-8'))
        else:
            self.send_headers()
            self.wfile.write(read_textfile('responses\\404.json').encode('utf-8'))


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port):
    mock_server = HTTPServer(('localhost', port), MockServerRequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()
