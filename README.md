# LaChain
A distributed system based on Lamport's mutual exclusion algorithm that uses blockchains as the process queue.

# Running the system

If you do not have applescript for python installed, run on terminal:
```sh
pip3 install applescript
```

Clone the repository and navigate to the repository root.

Startup the system by running:
```sh
python3 lachain.py
```

This terminal instance will function as the CLI for the system.

# LaChain CLI

### Server

View the balance table on the server terminal:
```sh
>>> balance server
```

### Clients

The valid client names are:
```
client_1
client_2
client_3
```

View the balance of the client on the client terminal:
```sh
>>> balance client <client_name>

example:
>>> balance client client_1
```

View the blockchain of the client on the client terminal:
```sh
>>> bchain <client_name>

example:
>>> bchain client_1
```

Issue a transfer transaction to a client:
```sh
>>> transfer <from_client_name> <to_client_name> <amount>

example:
>>> transfer client_1 client_2 5
```