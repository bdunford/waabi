#!/bin/bash

#belch
if [ "$1" == "belch" ]; then
    python run.py belch header -i ./tests/burps/burp-get.unenc.xml -o ./tests/outs/header-unenc.json
    python run.py belch header -i ./tests/burps/burp-get.enc.xml -o ./tests/outs/header-enc.json
    python run.py belch code -i ./tests/burps/burp-post.enc.xml -o ./tests/outs/run-post.py
    python run.py belch code -i ./tests/burps/burp-get.unenc.xml -o ./tests/outs/run-get.py
fi

if [ "$1" == "scan" ]; then
    read -n 1 -s -r -p "RUN: ./tests/hearken -p 8888"
    python run.py scan http://localhost:8888/ -H ./tests/header.json -w ./tests/words.txt 
fi

if [ "$1" == "wordlists" ]; then
    python run.py wordlists extract -o ./tests/outs/waabilists/
fi

