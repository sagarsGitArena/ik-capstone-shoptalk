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

#printf "\e[32m$(figlet -f slant 'Update')\e[0m"
figlet_print_green 'Ubuntu Update'
sudo apt update
figlet_print_green 'Ubuntu Upgrade'
#printf "\e[32m$(figlet -f slant 'Upgrade')\e[0m"
sudo apt upgrade -y

#printf "\e[32m$(figlet -f slant 'Install Docker')\e[0m"

figlet_print_green 'Install Docker'
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
sudo rm -f /usr/share/keyrings/docker-archive-keyring.gpg
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
sudo apt update
#printf "\e[32m$(echo -e 'Install the following : \n\t 1> Docker Community, \n\t 2> Docker CLI, \n\t 3> Container Runtime' | figlet -w 300 -f slant)\e[0m"
#
figlet_print_green 'Install the following : \n\t 1> Docker Community, \n\t 2> Docker CLI, \n\t 3> Container Runtime'
sudo apt install -y docker-ce docker-ce-cli containerd.io

#printf "\e[32m$(figlet -w 100 -f slant 'Verify Docker version')\e[0m" 
figlet_print_green 'Verify Docker version'
docker --version
sudo usermod -aG docker $USER

#printf "\e[32m$(figlet -w 200 -f slant 'Verify Docker Installation')\e[0m"
figlet_print_green 'Verify Docker Installation'
docker  run hello-world
id -nG
#exit
#ssh to the ec2 again
#docker run hello-world
#id -nG

#printf "\e[32m$(figlet -w 100 -f slant 'Install docker-compose')\e[0m"
figlet_print_green 'Install docker-compose'
echo "Y" | sudo apt install docker-compose
