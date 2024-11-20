# chatserver.py
import socket
import selectors
import types

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sel = selectors.DefaultSelector()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.server.setblocking(False)
        self.sel.register(self.server, selectors.EVENT_READ, data=None)
        self.running = True  # Nueva bandera para controlar el bucle

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()
        print(f"Conectado con {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)  # Intenta leer datos del socket
                if recv_data:
                    print(f"Recibido de {data.addr}: {recv_data.decode('ascii')}")
                    self.broadcast(recv_data, sock)
                else:  # Si no se recibe ningún dato, el cliente cerró la conexión
                    print(f"Cerrando conexión con {data.addr}")
                    self.sel.unregister(sock)
                    sock.close()
            except (ConnectionResetError, ValueError): 
                print(f"Error con conexión {data.addr}. Cerrando socket.")
                self.sel.unregister(sock)
                sock.close()
        elif mask & selectors.EVENT_WRITE:
            pass

    def broadcast(self, message, sender_sock):
        for key in list(self.sel.get_map().values()):
            client_sock = key.fileobj
            if client_sock is not self.server and client_sock is not sender_sock:
                try:
                    client_sock.send(message)
                except (BrokenPipeError, ConnectionResetError, ValueError):
                    print(f"Error al enviar mensaje. Cerrando conexión.")
                    self.sel.unregister(client_sock)
                    client_sock.close()


    def run(self):
        print(f"Servidor escuchando en {self.host}:{self.port}")
        try:
            while self.running:  # Bucle controlado por la bandera
                events = self.sel.select(timeout=1)  # Salimos cada segundo si no hay eventos
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Servidor detenido manualmente.")
        finally:
            self.stop()

    def stop(self):
        print("Deteniendo el servidor...")
        self.running = False 

        # Cerramos todas las conexiones registradas en el selector
        if self.sel and not self.sel._map == {}: 
            try:
                for key in list(self.sel.get_map().values()):
                    sock = key.fileobj
                    try:
                        print(f"Cerrando socket: {sock}")
                        self.sel.unregister(sock)
                    except KeyError:
                        print(f"Socket no estaba registrado: {sock}")
                    except Exception as e:
                        print(f"Error al intentar cerrar socket: {e}")
                    finally:
                        sock.close()
            except Exception as e:
                print(f"Error al manejar los sockets del selector: {e}")
            finally:
                try:
                    self.sel.close()
                    print("Selector cerrado.")
                except Exception as e:
                    print(f"Error al cerrar el selector: {e}")

        # Cerramos el socket principal del servidor
        if self.server:
            try:
                print("Cerrando socket principal del servidor...")
                self.server.close()
                print("Socket principal cerrado.")
            except Exception as e:
                print(f"Error al cerrar el socket principal: {e}")


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 55555
    server = ChatServer(host, port)
    server.run()
