#!/bin/bash
touch ~/.bash_git

echo '
if [ -e $HOME/.bash_git ]; then
    source $HOME/.bash_git
fi
' >> ~/.bashrc