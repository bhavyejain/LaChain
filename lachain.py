import subprocess
import applescript
import os
import time
import socket
import config
import threading

subprocess.call(['chmod', '+x', 'startup.sh'])

pwd = os.getcwd()
print(pwd)

applescript.tell.app("Terminal",f'do script "{pwd}/startup.sh server"')
time.sleep(0.5)
applescript.tell.app("Terminal",f'do script "{pwd}/startup.sh client client_1"')
time.sleep(1)
applescript.tell.app("Terminal",f'do script "{pwd}/startup.sh client client_2"')
time.sleep(1)

client_name = "CLI"

def receive():
    while True:
        message = client.recv(config.BUFF_SIZE).decode()
        print(f"{message}")

def send():
    while True:
        command = input("").strip()
        seg_cmd = command.split()
        if seg_cmd[0] == "server":
            print('Requesting server for balance sheet...')
            client.sendall(bytes("BALANCE", "utf-8"))

if __name__ == "__main__":

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.bind((config.HOST, config.CLI_PORT))

        client.connect((config.HOST, config.BANK_PORT))

        receive_thread = threading.Thread(target=receive)
        receive_thread.start()

        client.sendall(bytes(client_name, "utf-8"))

        send_thread = threading.Thread(target=send)
        send_thread.start()