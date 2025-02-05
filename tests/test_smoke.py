import os
import socket
import requests
from http import HTTPStatus


def test_status(app_url):
    response = requests.get(f"{app_url}/status")
    assert response.status_code == HTTPStatus.OK

def test_server_responds_on_port(port):
    local_host = os.getenv("HOST")
    with socket.create_connection((local_host, port), timeout=3):
        assert True, f"Server should be responding on port {port}."