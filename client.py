import socket
import threading
import config
import sys
from utils import Message, Transaction

connections = {}
client_name = ""
p_id = 0

def handle_client(client, client_id):
    client.sendall(bytes(f'Client {client_name} connected', "utf-8"))

    while True:
        try:
            message = client.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{client_id}: {message}')
            else:
                print(f'handle_client# Closing connection to {client_id}')
                client.close()
                break
        except:
            client.close()
            break

def handle_cli(client, client_id):
    client.sendall(bytes(f'Client {client_name} connected', "utf-8"))
    while True:
        try:
            message = client.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{client_id}: {message}')
                if message == "BALANCE":
                    connections['SERVER'].sendall(bytes("BALANCE", "utf-8"))
                    bal = connections["SERVER"].recv(config.BUFF_SIZE).decode()
                    print(f'Balance: {bal}')
            else:
                print(f'handle_cli# Closing connection to {client_id}')
                client.close()
                break
        except:
            client.close()
            break

def receive():
    while True:
        # Accept Connection
        client, addr = mySocket.accept()
        client.setblocking(True)
        client_id = client.recv(config.BUFF_SIZE).decode()
        print(f"receive# Connecting with {client_id}...")

        connections[client_id] = client
        
        if client_id == "CLI":
            target = handle_cli
        else:
            target = handle_client

        thread = threading.Thread(target=target, args=(client, client_id, ))
        thread.start()

if __name__ == "__main__":
    
    client_name = sys.argv[1]   # client_n
    p_id = int(client_name.split('_')[1])   # n

    print('================= BEGIN STARTUP =================')
    print(f'startup# Setting up Client {client_name} with process id {p_id}...')

    # connect to bank server
    print("startup# Connecting to server...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(True)
    server.connect((config.HOST, config.BANK_PORT))
    server.sendall(bytes(client_name, "utf-8"))
    print(f"startup# {server.recv(config.BUFF_SIZE).decode()}")

    connections['SERVER'] = server

    # connect to clients that have started up
    for n in range(1, p_id):
        client_tc = f'client_{n}'
        print(f'startup# Connecting to {client_tc}...')
        connections[client_tc] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connections[client_tc].connect((config.HOST, config.CLIENT_PORTS[client_tc]))
        connections[client_tc].setblocking(True)
        connections[client_tc].sendall(bytes(client_name, "utf-8"))
        print(f"startup# {connections[client_tc].recv(config.BUFF_SIZE).decode()}")
        thread = threading.Thread(target=handle_client, args=(connections[client_tc], client_tc,))
        thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mySocket:
        mySocket.bind((config.HOST, config.CLIENT_PORTS[client_name]))
        mySocket.listen(5)

        print('================= STARTUP COMPLETE =================')
        print('Listening for new connections...')

        receive()