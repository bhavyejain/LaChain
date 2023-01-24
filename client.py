import socket
import threading
import config
import sys

if __name__ == "__main__":
    
    client_name = sys.argv[1]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind((config.HOST, config.CLIENT_PORTS[client_name]))

    client.connect((config.HOST, config.BANK_PORT))
    client.sendall(bytes(client_name, "utf-8"))

    message = client.recv(config.BUFF_SIZE).decode()

    print(f"Message received: {message}")

    