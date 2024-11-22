# chatclient.py
import socket
from threading import Thread

class ChatClient:
    def __init__(self, nickname=None):
        self.nickname = nickname
        self.client = None
        
    def connect(self, host='127.0.0.1', port=55555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        
        if not self.nickname:
            self.nickname = input("Escriba su apodo: ")
            
        receiver_thread = Thread(target=self.receive, daemon=True)
        receiver_thread.start()
    
    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message:
                    print(message)
                else:
                    print("Conexión cerrada por el servidor")
                    self.client.close()
                    break
            except Exception as e:
                print(f"Error al recibir mensaje: {e}")
                self.client.close()
                break

    def write(self, default_message=None):
        try:
            if default_message:
                message = f'{self.nickname}: {default_message}'
                self.client.send(message.encode('ascii'))
                return True
            else:
                input_message = input('')
                if self.verify_message(input_message):
                    message = f'{self.nickname}: {input_message}'
                    self.client.send(message.encode('ascii'))
                    return True
                else:
                    print("Mensaje vacío")
                    return False
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
            self.client.close()
            return False

    def verify_message(self, message):
        return bool(message and message.strip())
        
    def close(self):
        if self.client:
            self.client.close()