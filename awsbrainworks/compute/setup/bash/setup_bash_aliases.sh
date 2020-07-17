#!/bin/bash
touch ~/.bash_aliases

echo '
if [ -e \$HOME/.bash_aliases ]; then
    source \$HOME/.bash_aliases
fi
' >> ~/.bashrc

echo '
# alias info
alias cd..='\''cd ..'\''
alias ..='\''cd ..'\''
alias ...='\''cd ../../../'\''
alias ....='\''cd ../../../../'\''
alias .....='\''cd ../../../../'\''
alias .4='\''cd ../../../../'\''
alias .5='\''cd ../../../../..'\''
' >> ~/.bash_aliases

echo '
# Colorize the grep command output for ease of use (good for log files)##
alias grep='\''grep --color=auto'\''
alias egrep='\''egrep --color=auto'\''
alias fgrep='\''fgrep --color=auto'\''
' >> ~/.bash_aliases

echo '
# shortcut for review
alias brc='\''cat ~/.bashrc'\''
alias bpf='\''cat ~/.bash_profile'\''
alias sbrc='\''source ~/.bashrc'\''
alias cbrc='\''code ~/.bashrc'\''
alias cbpf='\''code ~/.bash_profile'\''
alias cba='\''code ~/.bash_aliases'\''
alias cbf='\''code ~/.bash_functions'\''
' >> ~/.bash_aliases

echo '
# make dir is recursive and verbose by default
alias mkdir='\''mkdir -pv'\''
' >> ~/.bash_aliases

echo '
# convenience
alias h='\''history'\''
' >> ~/.bash_aliases

echo '
# show open ports
alias ports='\''netstat -tulanp'\''
' >> ~/.bash_aliases

echo '
# get system memory, cpu usage, and gpu memory info quickly
alias meminfo='\''free -m -l -t'\''
' >> ~/.bash_aliases

echo '
# get top process eating memory
alias psmem='\''ps auxf | sort -nr -k 4'\''
alias psmem10='\''ps auxf | sort -nr -k 4 | head -10'\''
' >> ~/.bash_aliases

echo '
# get top process eating cpu
alias pscpu='\''ps auxf | sort -nr -k 3'\''
alias pscpu10='\''ps auxf | sort -nr -k 3 | head -10'\''
' >> ~/.bash_aliases

echo '
# Get server cpu info
alias cpuinfo='\''lscpu'\''
' >> ~/.bash_aliases

echo '
# older system use /proc/cpuinfo
alias cpuinfo='\''less /proc/cpuinfo'\''
' >> ~/.bash_aliases

echo '
# get GPU ram on desktop / laptop
alias gpumeminfo='\''grep -i --color memory /var/log/Xorg.0.log'\''
' >> ~/.bash_aliases

echo '
# extend lsblk
alias lsblk='\''lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL,TYPE'\''
' >> ~/.bash_aliases