import socket
import threading
import config

clients = config.CLIENT_PORTS

balance_sheet = {}

def handle_client(client, client_id):
    client.sendall(bytes("Server connected", "utf-8"))

    while True:
        try:
            message = client.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{client_id}: {message}')

                if message.startswith("BALANCE"):
                    bal = balance_sheet[client_id]
                    print(f'Sending balance {bal} to {client_id}')
                    client.sendall(bytes(str(bal), "utf-8"))

                elif message.startswith("TRANSFER"):
                    transfer = message.split()  # ['TRANSFER', 'client_n', 'XX']
                    amount = int(transfer[2])
                    balance_sheet[client_id] = balance_sheet[client_id] - amount
                    balance_sheet[transfer[1]] = balance_sheet[transfer[1]] + amount

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
                if message == "BALANCE":
                    print(str(balance_sheet))
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
        client.setblocking(True)
        client_id = client.recv(config.BUFF_SIZE).decode()
        print(f"Connected with {client_id}")
        
        if client_id == "CLI":
            target = handle_cli
        else:
            target = handle_client
            balance_sheet[client_id] = 10

        thread = threading.Thread(target=target, args=(client, client_id, ))
        thread.start()

if (__name__ == "__main__"):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((config.HOST, config.BANK_PORT))
        server.listen(5)
        receive()