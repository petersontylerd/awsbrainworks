#!/bin/bash
# add environment variables and init commands
if ! command -v pyenv 1>/dev/null; then
echo '

# pyenv env variables and inits
export PYENV_ROOT=\$HOME/.pyenv
export PATH=\$PYENV_ROOT/bin:\$PATH
' >> ~/.bashrc

echo '
if command -v pyenv 1>/dev/null 2>&1; then
    eval "$(pyenv init -)"
fi

if command -v pyenv 1>/dev/null 2>&1; then
    eval "$(pyenv virtualenv-init -)"
fi
' >> ~/.bashrc

# ensure that virtualenv must be activate in order to run pip
echo '

# require virtualenv for pip
export PIP_REQUIRE_VIRTUALENV=true
export PYENV_VIRTUALENV_DISABLE_PROMPT=1
gpip() {
    PIP_REQUIRE_VIRTUALENV='\'''\'' pip '\''$@'\''
}' >> ~/.bashrc
fi