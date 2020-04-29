#!/bin/bash
if ! command -v pyenv 1>/dev/null; then
echo '
# pyenv env variables and inits
export PYENV_ROOT='\''$HOME/.pyenv'\''
export PATH='\''$PYENV_ROOT/bin:$PATH'\''
eval '\''$(pyenv init -)'\''
eval '\''$(pyenv virtualenv-init -)'\''
' >> ~/.bash_pyenv
fi

echo '
# require virtualenv for pip
export PIP_REQUIRE_VIRTUALENV=true
export PYENV_VIRTUALENV_DISABLE_PROMPT=1
gpip() {
    PIP_REQUIRE_VIRTUALENV='\'''\'' pip '\''$@'\''
}' >> ~/.bash_pyenv