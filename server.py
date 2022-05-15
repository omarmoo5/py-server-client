import socket
import threading
import mimetypes
from os import path

HOST = '127.0.0.1'
PORT = 80
TIMEOUT = 300

cache = {}

def handle_conn(conn, address):
    conn.settimeout(TIMEOUT) # static timeout for persistent connections
    print(f"Connected to {address}")

    while True: # for persistent connections

        try: data = conn.recv(1024)
        except (TimeoutError, ConnectionResetError): break
        if not data: break

        method, req, payload = parse_request_message(data)
        target = path.join('public', path.basename(req.split()[1]))

        print(f"Received a {method!r} request.")

        # check the cache
        a = cache.get(target)
        if a:
            print('Cache Hit.')
            conn.sendall(a)
            continue

        # miss
        if method == 'GET': handle_GET(target, conn)
        elif method == 'POST': handle_POST(target, payload, conn)

        # the request was served, wait for another

    conn.close()

def parse_request_message(data):
    data = data.split(b'\r\n\r\n')

    header = data[0].decode().split('\r\n')
    request = header[0]
    method = request.split()[0]

    body = data[1] if len(data) > 1 else None

    # print method and header options
    print(method)
    for line in header:
        print(line)

    return (method, request, body)

def handle_GET(target, conn):
    if path.isfile(target):
        res = (b'HTTP/1.0 200 OK\r\n' + 'Content-Type: {}\r\nContent-Length: {}\r\n\r\n'
        .format(mimetypes.guess_type(target)[0], path.getsize(target)).encode() +
        open(target, 'rb').read())
    else:
        res = b'HTTP/1.0 404 Not Found\r\n\r\n'
    
    cache[target] = res
    conn.sendall(res)

def handle_POST(target, payload, conn):
    with open(target, 'wb') as f:
        while payload is not None:
            f.write(payload)
            try: payload = conn.recv(1024)
            except (TimeoutError, ConnectionResetError): break

    conn.sendall(b'HTTP/1.0 200 OK\r\n')
    print(f'Created {target!r}')

if __name__ == '__main__':

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # for debugging
        s.bind((HOST, PORT))
        s.listen()
        while True:
            connection, address = s.accept()
            th = threading.Thread(target=handle_conn, args=[connection, address])
            th.start()
