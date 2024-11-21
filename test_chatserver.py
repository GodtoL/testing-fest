import socket
import threading
import pytest
from chatserver import ChatServer

@pytest.fixture
def start_server():
    server = ChatServer(host='127.0.0.1', port=55555)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    yield server
    server.stop()

@pytest.mark.parametrize("host, port, should_connect", [
    ("127.0.0.1", 55555, True),  # Caso positivo
    ("127.0.0.1", 12345, False),  # Caso negativo (puerto incorrecto)
    ("192.168.0.1", 55555, False),  # Caso negativo (host incorrecto)
])

def test_client_connection(start_server, host, port, should_connect):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        assert should_connect, f"Conexión exitosa con {host}:{port} cuando no debería ser posible."
    except (ConnectionRefusedError, TimeoutError) as e:
        assert not should_connect, f"Falló la conexión con {host}:{port} cuando debería haber sido posible. Error: {e}"
    finally:
        client.close()

def test_message_broadcast(start_server):
    # Creación de sockets de cliente
    client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clients = [client1, client2, client3, client4]

    try:
        # Conexión de todos los clientes
        for client in clients:
            client.connect(('127.0.0.1', 55555))
        
        # Envío de mensaje desde client1
        message = b"Hola clientes"
        client1.send(message)

        # Recepción de mensajes por los otros clientes
        received_messages = []
        for client in clients[1:]:
            client.settimeout(5)
            try:
                mess = client.recv(1024)
                received_messages.append(mess)
            except socket.timeout:
                print(f"Timeout al recibir mensaje en {client}")
                raise

        assert len(received_messages) == len(clients) - 1, "No se recibieron mensajes en todos los clientes"
        
        # Verificar que todos los mensajes recibidos son iguales
        assert all(mess == message for mess in received_messages), "Algunos clientes no recibieron el mensaje correcto"

    finally:
        # Cerrar las conexiones de los clientes
        for client in clients:
            client.close()

def test_multiple_clients_connection(start_server):
    clients = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(5)]
    try:
        for client in clients:
            client.connect(("127.0.0.1", 55555))
        assert all(client.fileno() != -1 for client in clients), "No todos los clientes se conectaron correctamente."
    finally:
        for client in clients:
            client.close()

def test_abrupt_disconnection(start_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 55555))
    client.close() 

    new_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_client.connect(("127.0.0.1", 55555))
    assert new_client.fileno() != -1
    new_client.close()
