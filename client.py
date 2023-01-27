import socket
import threading
import config
import sys
import time
from utils import Message, Transaction, LClock, Block, BlockChain, M_TYPE, RESULT
from threading import Lock

connections = {}
client_name = ""
p_id = 0
reply_count = 0
blockchain = BlockChain()
b_lock = Lock() # lock for blockchain modification
REQ_REP = len(config.CLIENT_PORTS) - 1

def get_pid(client_name):
    return int(client_name.split('_')[1])

def send_to_client(message, client_n, delay=config.DEF_DELAY):
    print(f'Sending {message.messageType.name} message with clock {message.clock.__str__()} to {client_n}')
    time.sleep(delay)
    connections[client_n].sendall(bytes(message.__str__(), "utf-8"))

def broadcast_to_clients(message):
    print('Starting broadcast...')
    time.sleep(2)
    for client in connections.keys():
        if client != "SERVER" and client != "CLI":
            send_to_client(message, client, 0)

def job_worker():
    global reply_count

    print('Starting job worker...')
    print(f'Requires replies per transaction: {REQ_REP}')
    while True:
        with b_lock:
            block = blockchain.current()
            # print(f'WORKER: curr_client:{blockchain.current_client()} | reply_count:{reply_count}')
            if blockchain.current_client() == client_name and not block.is_resolved() and reply_count >= REQ_REP:
                print(f'========== Executing Transfer ==========')
                reply_count -= REQ_REP
                transaction = block.transaction
                print(f'Transaction: {transaction.__str__()}')
                connections['SERVER'].sendall(bytes("BALANCE", "utf-8"))
                bal = connections["SERVER"].recv(config.BUFF_SIZE).decode()
                print(f'Balance: {bal}')
                if int(bal) < int(transaction.amount):
                    print("FAILED")
                    blockchain.resolve_current(RESULT.ABORTED)
                    result = RESULT.ABORTED
                else:
                    print("SUCCESS")
                    connections['SERVER'].sendall(bytes(f"TRANSFER {transaction.destination} {transaction.amount}", "utf-8"))
                    blockchain.resolve_current(RESULT.SUCCESS)
                    result = RESULT.SUCCESS
                release = Message(messageType=M_TYPE.RELEASE, source=client_name, clock=clock, req_clock=block.timestamp, status=result)
                broadcast_to_clients(release)
                print(f'========== Operation Complete ==========')
        time.sleep(1)

def handle_client(client, client_id):
    client.sendall(bytes(f'Client {client_name} connected', "utf-8"))

    while True:
        try:
            raw_message = client.recv(config.BUFF_SIZE).decode()
            if raw_message:
                print(f'{client_id}: {raw_message}')
                if raw_message.startswith("Client"):
                    continue

                message = Message.getFromString(raw_message)
                if message.messageType == M_TYPE.MUTEX:
                    clock.update(message.clock)
                    block = Block(message.clock, message.transaction)
                    with b_lock:
                        blockchain.insert(block)
                    reply = Message(messageType=M_TYPE.REPLY, source=client_name, clock=clock, req_clock=message.clock)
                    send_to_client(reply, client_id)
                elif message.messageType == M_TYPE.REPLY:
                    global reply_count
                    reply_count = reply_count + 1
                elif message.messageType == M_TYPE.RELEASE:
                    with b_lock:
                        blockchain.resolve_current(message.status)

            else:
                print(f'handle_client# Closing connection to {client_id}')
                client.close()
                break
        except Exception as e:
            print(f'handle_client# Exception caused, closing connection to {client_id}')
            print(f'Exception: {e.__str__()}, Traceback: {e.__traceback__()}')

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
                elif message == "BLOCKCHAIN":
                    blockchain.print_chain()
                elif message.startswith("TRANSFER"):
                    cmd = message.split()
                    transaction = Transaction(client_name, cmd[1], cmd[2])
                    timestamp = clock.increment()
                    block = Block(timestamp, transaction)
                    with b_lock:
                        blockchain.insert(block)
                    print(f'Created transaction: {transaction}')
                    message = Message(messageType=M_TYPE.MUTEX, source=client_name, clock=timestamp, transaction=transaction)
                    print(f'Broadcasting message: {message.__str__()}')
                    broadcast_to_clients(message)
            else:
                print(f'handle_cli# Closing connection to {client_id}')
                client.close()
                break
        except Exception as e:
            print(f'handle_cli# Exception caused, closing connection to {client_id}')
            print(f'Exception: {e.__str__()}, Traceback: {e.__traceback__()}')

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

def connect_running_clients():
    for n in range(1, p_id):
        client_tc = f'client_{n}'
        print(f'startup# Connecting to {client_tc}...')
        try:
            connections[client_tc] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connections[client_tc].connect((config.HOST, config.CLIENT_PORTS[client_tc]))
            connections[client_tc].setblocking(True)
            connections[client_tc].sendall(bytes(client_name, "utf-8"))
            print(f"startup# {connections[client_tc].recv(config.BUFF_SIZE).decode()}")
            thread = threading.Thread(target=handle_client, args=(connections[client_tc], client_tc,))
            thread.start()
        except:
            print(f'startup# Failed to connect to {client_tc}!')

if __name__ == "__main__":
    
    client_name = sys.argv[1]   # client_n
    p_id = get_pid(client_name)   # n
    global clock
    clock = LClock(time=0, pid=p_id)

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
    connect_running_clients()

    worker_thread = threading.Thread(target=job_worker, args=())
    worker_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mySocket:
        mySocket.bind((config.HOST, config.CLIENT_PORTS[client_name]))
        mySocket.listen(5)

        print('================= STARTUP COMPLETE =================')
        print('Listening for new connections...')

        receive()