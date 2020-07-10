#!/bin/bash
touch ~/.bash_git

echo '
if [ -e \$HOME/.bash_git ]; then
    source \$HOME/.bash_git
fi
' >> ~/.bashrc

echo '
git config --global user.email '\''petersontylerd@gmail.com'\''
git config --global user.name '\''Tyler Peterson'\''
' >> ~/.bash_git