import os, sys

HOST = "0.0.0.0"
HTTP_PORT = 5000
SOCKET_PORT = 5001
URI = f"http://{HOST}:{HTTP_PORT}"

SSL_CONTEXT = "adhoc"

if len(sys.argv) == 3:
    # SSL_CERT = os.environ["SSL_CERT"]
    # SSL_KEY = os.environ["SSL_KEY"]

    SSL_CERT = sys.argv[1]
    SSL_KEY = sys.argv[2]


    SSL_CONTEXT = (SSL_CERT, SSL_KEY)
    URI = f"https://{HOST}:{HTTP_PORT}"
