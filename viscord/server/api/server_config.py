import os

HOST = "0.0.0.0"
PORT = 5000
URI = f"http://{HOST}:{PORT}"

SSL_CONTEXT = "adhoc"

if "SSL_CERT" in os.environ and "SSL_KEY" in os.environ:
    SSL_CERT = os.environ["SSL_CERT"]
    SSL_KEY = os.environ["SSL_KEY"]
    SSL_CONTEXT = (SSL_CERT, SSL_KEY)
    URI = f"https://{HOST}:{PORT}"