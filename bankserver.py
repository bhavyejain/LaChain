import socket
import threading
import config

clients = config.CLIENT_PORTS

balance_sheet = {}

def handle_client(client_socket, client_id):
    client_socket.sendall(bytes("Server connected", "utf-8"))
    while True:
        try:
            message = client_socket.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{client_id}: {message}')

                if message.startswith("BALANCE"):
                    client_socket.sendall(bytes(balance_sheet[client_id], "utf-8"))

                elif message.startswith("TRANSFER"):
                    transfer = message.split()  # ['TRANSFER', 'client_n', 'XX']
                    amount = int(transfer[2])
                    balance_sheet[client_id] = balance_sheet[client_id] - amount
                    balance_sheet[transfer[1]] = balance_sheet[transfer[1]] + amount

            else:
                print(f'Closing connection to {client_id}')
                client_socket.close()
                break
        except:
            index = clients.index(client_socket)
            clients.remove(client_socket)
            client_socket.close()
            break

def handle_cli(client_socket, client_id):
    client_socket.sendall(bytes("Server connected", "utf-8"))
    while True:
        try:
            message = client_socket.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{client_id}: {message}')
                if message == "BALANCE":
                    client_socket.sendall(bytes(str(balance_sheet), "utf-8"))
            else:
                print(f'Closing connection to {client_id}')
                client_socket.close()
                break
        except:
            client_socket.close()
            break

def receive():
    while True:
        # Accept Connection
        client_socket, addr = server.accept()
        client_id = client_socket.recv(config.BUFF_SIZE).decode()
        print(f"Connected with {client_id}")
        
        if client_id == "CLI":
            target = handle_cli
        else:
            target = handle_client
            balance_sheet[client_id] = 10

        thread = threading.Thread(target=target, args=(client_socket, client_id, ))
        thread.start()

if (__name__ == "__main__"):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((config.HOST, config.BANK_PORT))
        server.listen(5)
        receive()