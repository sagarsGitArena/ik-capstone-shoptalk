!#/bin/bash

figlet_print_red() {
#    printf "\e[31m$(echo -e "$1" | figlet -w 300 -f slant)\e[0m"
    printf "\e[31m$(figlet -w 300 -f slant "$1")\e[0m"
    echo ""
}



if ! dpkg -l | grep -q figlet; then
    sudo apt update
    sudo apt install -y figlet
else
    echo "Figlet is already installed."
fi
#printf "\e[31m$(figlet Docker Installation )\e[0m"
figlet_print_red "Docker Installation"
./set-up/.set-up-env-1.sh
#figlet_print_red 'NVIDIA - Pre-requisite'
#./set-up/.nvidia-pre-req.sh
figlet_print_red 'NVIDIA - Docker Upgrade'
./set-up/.set-up-env-2.sh
figlet_print_red 'Set Up Complete'
