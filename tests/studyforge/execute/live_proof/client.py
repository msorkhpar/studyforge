"""The live runner's side of the proof: direct connections, then connections through the proxy."""

import socket
import sys


def connect(target, host, port):
    s = socket.create_connection((host, port), 5)
    s.sendall(f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
    head = s.recv(4096).split(b"\r\n")[0].decode()
    body = ""
    if " 200 " in head:
        s.sendall(b"GET / HTTP/1.0\r\n\r\n")
        s.settimeout(5)
        raw = b""
        try:
            while chunk := s.recv(4096):
                raw += chunk
        except OSError:
            pass
        body = raw.decode(errors="replace").split("\r\n\r\n")[-1].strip()
    return head, body


def direct(host, port):
    try:
        socket.create_connection((host, port), 3).close()
        return "CONNECTED"
    except Exception as error:
        return type(error).__name__


proxy, standin_ip = sys.argv[1], sys.argv[2]
print("direct allowed.test:443       ->", direct("allowed.test", 443))
print("direct stand-in ip:443        ->", direct(standin_ip, 443))
print("direct 1.1.1.1:443 (internet) ->", direct("1.1.1.1", 443))
print("via proxy allowed.test:443    ->", connect("allowed.test:443", proxy, 3128))
print("via proxy denied.test:443     ->", connect("denied.test:443", proxy, 3128))
print("via proxy allowed.test:80     ->", connect("allowed.test:80", proxy, 3128))
print("via proxy 127.0.0.1:443       ->", connect("127.0.0.1:443", proxy, 3128))
