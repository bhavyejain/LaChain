import socket
import threading
import config
from utils import Colors as c

clients = config.CLIENT_PORTS

balance_sheet = {}

def handle_client(client, client_id):
    client.sendall(bytes("Server connected", "utf-8"))
    while True:
        try:
            message = client.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{c.VIOLET}{client_id}{c.ENDC}: {message}')

                if message.startswith("BALANCE"):
                    bal = balance_sheet[client_id]
                    print(f'Sending balance ${bal} to {client_id}')
                    client.sendall(bytes(str(bal), "utf-8"))

                elif message.startswith("TRANSFER"):
                    transfer = message.split()  # ['TRANSFER', 'client_n', 'XX']
                    amount = int(transfer[2])
                    balance_sheet[client_id] = balance_sheet[client_id] - amount
                    balance_sheet[transfer[1]] = balance_sheet[transfer[1]] + amount
                    print(f'Transferred ${amount} from {client_id} to {transfer[1]}.')
            else:
                print(f'Closing connection to {client_id}')
                client.close()
                break
        except Exception as e:
            print(f'{c.ERROR}handle_client# Exception thrown in {client_id} thread!{c.ENDC}')
            print(f'Exception: {e.__str__()}, Traceback: {e.__traceback__()}')

def handle_cli(client, client_id):
    client.sendall(bytes("Server connected", "utf-8"))
    while True:
        try:
            message = client.recv(config.BUFF_SIZE).decode()
            if message:
                print(f'{c.VIOLET}{client_id}:{c.ENDC} {message}')
                if message == "BALANCE":
                    print(f"===== {c.SELECTED}ACCOUNT INFO{c.ENDC} =====")
                    for c_name, bal in balance_sheet.items():
                        print(f'{c.BLUE}{c_name}{c.ENDC}  :\t {bal}')
                    print("========================")
            else:
                print(f'Closing connection to {client_id}')
                client.close()
                break
        except Exception as e:
            print(f'{c.ERROR}handle_cli# Exception thrown in {client_id} thread!{c.ENDC}')
            print(f'Exception: {e.__str__()}, Traceback: {e.__traceback__()}')

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
            balance_sheet[client_id] = config.INIT_BALANCE

        thread = threading.Thread(target=target, args=(client, client_id,))
        thread.start()

if (__name__ == "__main__"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((config.HOST, config.BANK_PORT))
        server.listen(5)
        print(f'================= SERVER STARTUP COMPLETE =================')
        print('Listening for new connections...')
        receive()