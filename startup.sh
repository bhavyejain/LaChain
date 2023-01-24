#!/usr/bin/env bash

cd "/Users/bhavye/Documents/DistributedSystems/LaChain"

if [ "$1" = "server" ]
then
    echo -n -e "\033]0;bank server\007"
    echo "Starting bank server..."
    python3 bankserver.py
fi

if [ "$1" = "client" ]
then
    echo -n -e "\033]0;$2\007"
    echo "Starting client $2..." 
    python3 client.py $2
fi
