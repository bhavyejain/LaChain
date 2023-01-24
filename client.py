import socket
import threading
import config
import sys
from utils import Request, Transaction

connections = {}
client_name = ""

def handle_client(client, client_id):
    client.sendall(bytes("Server connected", "utf-8"))

    while True:
        try:
            message = client.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{client_id}: {message}')

            else:
                print(f'Closing connection to {client_id}')
                client.close()
                break
        except:
            client.close()
            break

def handle_cli(client, client_id):
    client.sendall(bytes("Server connected", "utf-8"))
    while True:
        try:
            message = client.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{client_id}: {message}')
            else:
                print(f'Closing connection to {client_id}')
                client.close()
                break
        except:
            client.close()
            break

def receive():
    while True:
        # Accept Connection
        client, addr = server.accept()
        client.setblocking(False)
        client_id = client.recv(config.BUFF_SIZE).decode()
        print(f"Connected with {client_id}")
        
        if client_id == "CLI":
            target = handle_cli
        else:
            target = handle_client

        thread = threading.Thread(target=target, args=(client, client_id, ))
        thread.start()

if __name__ == "__main__":
    
    client_name = sys.argv[1]

    # connect to bank server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((config.HOST, config.BANK_PORT))
    server.sendall(bytes(client_name, "utf-8"))
    print(f"Message received: {server.recv(config.BUFF_SIZE).decode()}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.bind((config.HOST, config.CLIENT_PORTS[client_name]))
        client.listen(5)
        receive()