import unittest
import socket
import threading
import time
from chatserver import ChatServer

def test_client_connection():
        # Prueba si un cliente puede conectarse al servidor
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 55555))
        assert client
    finally:
        client.close()

# def test_message_broadcast():
#     client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client2 = socket.socket(socket.AddressFamily, socket.SOCK_STREAM)
#     try:
#         client1.connect('127.0.0.1', 55555)
#         client2.connect('127.0.0.1', 55555)

#         message = b"Hola client2"
#         client1.send(message)

#         mess = client2.recv()
#         assert mess == message
#     finally:
#         client1.close()
#         client1.close()
