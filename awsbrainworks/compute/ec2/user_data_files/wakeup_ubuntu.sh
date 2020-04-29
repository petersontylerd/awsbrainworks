#!/bin/bash
apt-get update -y
apt-get upgrade -y

sudo apt-get install -y \
    awscli \
    build-essential \
    bzip2 \
    curl \
    dos2unix \
    git \
    htop \
    libbz2-dev \
    libffi-dev \
    libgdbm-compat-dev \
    libgdbm-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    nano \
    net-tools \
    openssl \
    python3-pip \
    python3.7 \
    software-properties-common \
    sqlite3 \
    ssh \
    tree \
    uuid-dev \
    zlib1g-dev \

apt-get clean

echo 'done' >> /tmp/testfile.txt