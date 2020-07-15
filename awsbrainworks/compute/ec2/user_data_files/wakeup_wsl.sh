#!/bin/sh
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y \
    awscli \
    build-essential \
    net-tools \
    python3-pip \
    software-properties-common \
    tree