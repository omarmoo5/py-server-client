import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 80  # The port used by the server

# file = open("logo.png", "rb")
# byte = file.read(3)
# while byte:
#     print(byte)
#     byte = file.read(3)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall("POST bla bla bla".encode())
    data = s.recv(1024)

print(f"Received {data!r}")