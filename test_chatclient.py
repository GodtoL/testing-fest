# test_chatclient.py
import pytest
import socket
import time
from threading import Thread, Event
from chatclient import ChatClient

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

@pytest.fixture
def server():
    port = find_free_port()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.listen()
    
    def accept_and_echo():
        client, _ = server.accept()
        while True:
            try:
                msg = client.recv(1024)
                if msg:
                    client.send(msg)
            except:
                break
            
    Thread(target=accept_and_echo, daemon=True).start()
    time.sleep(0.1)
    
    yield server, port
    
    try:
        server.close()
    except:
        pass

def test_write_and_receive(server):
    server_socket, port = server
    
    # Variables para capturar el mensaje
    received_messages = []
    message_received = Event()
    should_stop = Event()
    
    class TestChatClient(ChatClient):
        def receive(self):
            while not should_stop.is_set():
                try:
                    message = self.client.recv(1024).decode('ascii')
                    if message:
                        received_messages.append(message)
                        message_received.set()
                except socket.error:
                    break
    
    client = TestChatClient(nickname="TestUser")
    client.connect(port=port)
    
    test_message = "Hola servidor"
    client.write(test_message)
    
    message_received.wait(timeout=2.0)
    
    expected = f"TestUser: {test_message}"
    assert received_messages[0] == expected
    
    should_stop.set()
    client.close()

def test_void_message():
    client = ChatClient()
    message = ""
    assert not client.verify_message(message)