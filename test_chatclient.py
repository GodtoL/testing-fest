import socket
from chatserver import ChatServer

def test_write():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55555))

    message = b'hello'
    assert client.send(message)