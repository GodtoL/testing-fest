import unittest
import socket
import threading
import time
from chatserver import ChatServer

class TestChatServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Inicia el servidor en un hilo separado
        host = '127.0.0.1'
        port = 55555
        cls.server = ChatServer(host, port)
        cls.server_thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.server_thread.start()
        time.sleep(1)  # Espera a que el servidor inicie

    def test_client_connection(self):
        # Prueba si un cliente puede conectarse al servidor
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.server.host, self.server.port))
            self.assertTrue(client)
        finally:
            client.close()

    def test_message_broadcast(self):
        # Prueba si los mensajes se retransmiten a otros clientes
        client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client1.connect((self.server.host, self.server.port))
            client2.connect((self.server.host, self.server.port))

            message = b"Hello from client1"
            client1.send(message)

            # Recibe el mensaje en el cliente 2
            received = client2.recv(1024)
            self.assertEqual(received, message)
        finally:
            client1.close()
            client2.close()

    @classmethod
    def tearDownClass(cls):
        print("Deteniendo el servidor desde las pruebas...")
        cls.server.stop()  # Detenemos el servidor
        cls.server_thread.join(timeout=5)  # Asegúrate de que el hilo se una
        print("Servidor detenido.")


if __name__ == "__main__":
    unittest.main()