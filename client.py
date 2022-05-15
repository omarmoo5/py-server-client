import socket
import mimetypes
from sys import argv
from os import path, getcwd

TIMEOUT = 10

input_file = argv[1] if len(argv) > 1 else 'test_requests.txt'
input_file = open(input_file, 'r')
prev_port = None
sock = None

for request in input_file.readlines():

    port = 80 # default port

    s = request.split()
    if len(s) == 4: method, filename, hostname, port = s
    elif len(s) == 3: method, filename, hostname = s
    else: continue # bad line

    if method == 'POST' and not path.isfile(filename): continue

    # valid request
    port = int(port)
    print(request)

    while True: # just a goto
        retry = False
        out = False

        # create a new connection or use old one?
        if not sock or prev_port != port:
            prev_port = port
            if sock: sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # new

            try: sock.connect((hostname, port))
            except ConnectionRefusedError:
                sock = None
                out = True
                break # bad port

            sock.settimeout(TIMEOUT)

        prev_port = port

        if method == 'GET':
            first = True
            ff = None
            length_so_far = 0
            length = None

            sock.sendall(f'GET /{filename} HTTP/1.1\r\n'.encode())
            while True:

                try: data = sock.recv(1024)
                except (TimeoutError, ConnectionResetError):
                    retry = True
                    break # must re-request
                if not data: raise Exception('Very Weird') # should never happen

                if first:
                    data = data.split(b'\r\n\r\n')
                    header = data[0].decode().split('\r\n')
                    if header[0].split()[1] == '404': break
                    if not length:
                        for c in header:
                            c = c.split(':')
                            if c[0] == 'Content-Length':
                                length = int(c[1])
                                break

                    if len(data) == 1: continue # long header
                    data = data[1]
                    first = False

                if not ff: ff = open(filename, 'wb')
                ff.write(data)

                length_so_far += len(data)
                if length_so_far == length: break # complete file received

            if ff: ff.close()

        else: # method == 'POST'
            af = filename
            filename = path.join(getcwd(), filename)
            ff = open(filename, 'rb')
            sock.sendall('POST /{} HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\n\r\n'
            .format(af, mimetypes.guess_type(filename)[0], path.getsize(filename)).encode() + ff.read())
            ff.close()
        
        if out: continue
        if not retry: break

if s: sock.close()
input_file.close()
