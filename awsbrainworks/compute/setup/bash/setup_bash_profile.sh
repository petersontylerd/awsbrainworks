#!/bin/bash

echo '
if [ -e \$HOME/.bash_profile ]; then
    source \$HOME/.bash_profile
fi
' >> ~/.bashrc

echo '
export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagaced
' >> ~/.bash_profile