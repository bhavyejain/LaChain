#!/usr/bin/env bash

cd "/Users/bhavye/Documents/DistributedSystems/LaChain"

if [ "$1" = "server" ]
then
    echo "Starting bank server..."
    python3 bankserver.py
fi

if [ "$1" = "client" ]
then
    echo "Starting client $2..." 
    python3 client.py $2
fi
