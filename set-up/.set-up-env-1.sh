#!/bin/bash


figlet_print_green() {
    # "$1" gets the first argument passed to the function
    printf "\e[32m$(echo -e "$1" | figlet -w 300 -f slant)\e[0m"
    echo ""
}


if ! dpkg -l | grep -q figlet; then
    sudo apt update
    sudo apt install -y figlet
else
    echo "Figlet is already installed."
fi


figlet_print_green 'Ubuntu Update'
sudo apt update
figlet_print_green 'Ubuntu Upgrade'

sudo apt upgrade -y



figlet_print_green 'Install Docker'
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

sudo rm -f /usr/share/keyrings/docker-archive-keyring.gpg
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 

sudo apt update

figlet_print_green 'Install Docker Components'
sudo DEBIAN_FRONTEND=noninteractive apt install -y docker-ce docker-ce-cli containerd.io
#sudo apt install -y docker-ce docker-ce-cli containerd.io

figlet_print_green 'Verify Docker version'
docker --version

# Add user to docker group
sudo usermod -aG docker $USER

figlet_print_green 'Verify Docker Installation'

# Use sudo to avoid permission issues immediately
sudo docker run hello-world

# Optional: Warn the user that logout/login is needed for no-sudo Docker
echo -e "\e[33m⚠️  If you want to run Docker without sudo, you need to log out and back in or run:\n    newgrp docker\e[0m"

id -nG

figlet_print_green 'Install docker-compose'
echo "Y" | sudo apt install docker-compose




