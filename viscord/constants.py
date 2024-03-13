SERVER = "trigtbh.dev" # your mileage may vary on this being the actual server you use (and thus it being a *constant*) but for now this is what we got
PORT = 5000

import socket
CONNECTION = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CONNECTION.connect((SERVER, PORT))

