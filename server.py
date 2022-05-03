import socket
import threading


def handle_conn(connection, address):
    with connection:
        print(f"Connected by {address}")
        while True:
            data = connection.recv(1024)
            print(f"Received {data!r}")
            if not data:
                break
            connection.sendall(data)


if __name__ == '__main__':
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 80  # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            connection, address = s.accept()
            th = threading.Thread(target=handle_conn, args=[connection, address])
            th.start()
