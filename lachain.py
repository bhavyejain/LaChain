import subprocess
import applescript
import os
import time
import socket
import config
import threading

subprocess.call(['chmod', '+x', 'startup.sh'])

pwd = os.getcwd()
print("================= STARTING LACHAIN =================")

print("Starting bank server...")
applescript.tell.app("Terminal",f'do script "{pwd}/startup.sh server"')
time.sleep(0.5)
'''
print("Starting client_1...")
applescript.tell.app("Terminal",f'do script "{pwd}/startup.sh client client_1"')
time.sleep(0.5)
print("Starting client_2...")
applescript.tell.app("Terminal",f'do script "{pwd}/startup.sh client client_2"')
time.sleep(0.5)
print("Starting client_3...")
applescript.tell.app("Terminal",f'do script "{pwd}/startup.sh client client_3"')
time.sleep(0.5)
'''

client_name = "CLI"

connections = {}

def receive(app):
    app.sendall(bytes(f'Client {client_name} connected', "utf-8"))
    while True:
        try:
            message = app.recv(config.BUFF_SIZE).decode()
            if not message:
                app.close()
                break
        except:
            app.close()
            break

def send():
    while True:
        command = input(">>> ").strip()
        seg_cmd = command.split()
        app = seg_cmd[0]
        if app == "server":
            connections[app].sendall(bytes("BALANCE", "utf-8"))
        elif app == "client":
            print(f'')

def connect_to(name, port):
    print(f'startup# Connecting to {name}...')
    connections[name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections[name].setblocking(True)
    connections[name].connect((config.HOST, port))
    connections[name].sendall(bytes(client_name, "utf-8"))
    print(f"startup# {connections[name].recv(config.BUFF_SIZE).decode()}")
    thread = threading.Thread(target=receive, args=(connections[name],))
    thread.start()

if __name__ == "__main__":

    connect_to("server", config.BANK_PORT)
    '''
    for client, port in config.CLIENT_PORTS.items():
        connect_to(client, port)
    '''

    print("================= SETUP COMPLETE =================")

    #send_thread = threading.Thread(target=send)
    #send_thread.start()
    send()