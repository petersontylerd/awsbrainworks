#! /bin/bash
# install python itself
pyenv install 3.7.7
pyenv global 3.7.7

# create virtualenv
pyenv virtualenv 3.7.7 main37

# reset terminal
exec "$SHELL"