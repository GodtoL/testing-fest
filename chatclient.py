import socket
import threading
import sys

nickname = input("Escriba su apodo: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message:
                print(message)
            else:
                print("Conexión cerrada por el servidor")
                client.close()
                break
        except:
            print("Error fatal al recibir mensaje")
            client.close()
            break

def write():
    while True:
        try:
            input_message = input('')
            if input_message.strip():
                message = f'{nickname}: {input_message}'
                client.send(message.encode('ascii'))
        except EOFError:
            print("Conexión cerrada por el cliente")
            client.close()
            break
        except:
            print("Error fatal al enviar mensaje")
            client.close()
            break

receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
