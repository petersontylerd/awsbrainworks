#!/bin/sh
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y \
    awscli \
    apt-transport-https \
    build-essential \
    bzip2 \
    curl \
    git \
    gnupg-agent \
    htop \
    jq \
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
    nodejs \
    npm \
    openssl \
    openjdk-8-jdk \
    openjdk-8-jre \
    python3-pip \
    python3.7 \
    software-properties-common \
    ssh \
    tree \
    uuid-dev \
    zlib1g-dev
echo 'done' >> /tmp/testfile.txt