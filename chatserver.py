
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
        try:
            conn, addr = sock.accept()  # Acepta la conexión
            print(f"Conectado con {addr}")
            conn.setblocking(False)
            data = types.SimpleNamespace(addr=addr)
            self.sel.register(conn, selectors.EVENT_READ, data=data)
        except (OSError, ValueError) as e:
            print(f"Error al aceptar conexión: {e}")

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data  # Información adicional asociada al cliente

        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(1024)  # Intenta leer datos del socket
                if recv_data:
                    print(f"Recibido de {data.addr}: {recv_data.decode('ascii')}")
                    self.broadcast(recv_data, sock)
                else:
                    # Si no se recibe ningún dato, el cliente cerró la conexión
                    print(f"Cerrando conexión con {data.addr}")
                    self.close_connection(sock)

            except (OSError, ConnectionResetError, BlockingIOError) as e:  # Se añade BlockingIOError
                print(f"Error con conexión {data.addr}: {e}. Cerrando socket.")
                self.close_connection(sock)

        elif mask & selectors.EVENT_WRITE:
            # Aquí podrías manejar la escritura si fuese necesario
            pass

    def close_connection(self, sock):
        # Asegurarse de que el socket esté registrado antes de desregistrarlo
        try:
            if sock.fileno() != -1:  # Verifica si el socket está abierto
                if sock.fileno() in self.sel.get_map():  # Uso de fileno en lugar de sock
                    print(f"Desregistrando socket {sock.getpeername()}")
                    self.sel.unregister(sock)
                sock.close()
                print(f"Conexión cerrada con {sock.getpeername()}")
            else:
                print(f"El socket {sock.getpeername()} ya está cerrado.")
        except ValueError:
            print(f"Error: El socket {sock} ya está cerrado o desregistrado.")
        except OSError:
            print(f"Error al acceder a {sock} porque ya está cerrado o no es un socket válido.")

    def broadcast(self, message, sender_sock):
        for key in list(self.sel.get_map().values()):
            client_sock = key.fileobj
            if client_sock is not self.server and client_sock is not sender_sock:
                try:
                    client_sock.send(message)
                except (BrokenPipeError, ConnectionResetError, ValueError, OSError) as e:
                    print(f"Error al enviar mensaje a {client_sock}: {e}. Cerrando conexión.")
                    # Cerramos el socket solo si está registrado
                    try:
                        if client_sock.fileno() != -1 and client_sock.fileno() in self.sel.get_map():
                            self.sel.unregister(client_sock)
                            client_sock.close()
                    except ValueError:
                        print(f"Error al desregistrar socket {client_sock}: ya está cerrado o desregistrado.")
                    except OSError:
                        print(f"Error al cerrar socket {client_sock}: ya está cerrado o no es un socket válido.")

    def run(self):
        print(f"Servidor escuchando en {self.host}:{self.port}")
        try:
            while self.running:  # Bucle controlado por la bandera
                if self.sel.get_map():
                    events = self.sel.select(timeout=1)
                    if events:
                        for key, mask in events:
                            if key.data is None:
                                self.accept_wrapper(key.fileobj)
                            else:
                                self.service_connection(key, mask)
                    else:
                        print("No hay eventos disponibles. Finalizando...")
                else:
                    print("Selector cerrado o vacío.")
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
