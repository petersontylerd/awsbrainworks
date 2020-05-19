#!/bin/bash
touch ~/.bash_functions

echo '
if [ -e \$HOME/.bash_functions ]; then
    source \$HOME/.bash_functions
fi
' >> ~/.bashrc