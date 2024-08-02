import socket
import selectors
import types

host = '127.0.0.1'
port = 55555

# Creamos el selector
sel = selectors.DefaultSelector()

# Configuración del socket del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"Servidor escuchando en {host} : {port}")

# Configuramos el socket como no bloqueante
server.setblocking(False)

# Registramos el socket en el selector
sel.register(server, selectors.EVENT_READ, data=None)

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Conectado con {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)
            if recv_data:
                print(f"Recibido de {data.addr}: {recv_data.decode('ascii')}")
                broadcast(recv_data, sock)
            else:
                print(f"Cerrando conexión con {data.addr}")
                sel.unregister(sock)
                sock.close()
        except ConnectionResetError:
            print(f"Conexión cerrada por {data.addr}")
            sel.unregister(sock)
            sock.close()

def broadcast(message, sender_sock):
    for key in sel.get_map().values():
        client_sock = key.fileobj
        if client_sock is not server and client_sock is not sender_sock:
            try:
                client_sock.send(message)
            except BrokenPipeError:
                print(f"Error al enviar a {key.data.addr}")
                sel.unregister(client_sock)
                client_sock.close()

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Cerrando servidor")
finally:
    sel.close()
