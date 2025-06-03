#!/bin/bash


figlet_printf_green() {
    # "$1" gets the first argument passed to the function
    printf "\e[32m$(echo -e $1 | figlet -w 300 -f slant)\e[0m"
    echo ""
}



if ! dpkg -l | grep -q figlet; then
    sudo apt update
    sudo apt install -y figlet
else
    echo "Figlet is already installed."
fi
###### NVIDIA - DOCKER installation to leverage host GPUs #########
#printf "NVIDIA - DOCKER Installation" | figlet -w 200
#printf "\e[32m$(echo -e 'Install NVIDIA-DOCKER' | figlet -w 300 -f slant)\e[0m"
#echo ""

figlet_printf_green 'NVIDIA  Docker'
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && \
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && \
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update

figlet_printf_green 'Install nvidia-docker2'
sudo apt-get install -y nvidia-docker2


#printf "\e[32m$(echo -e 'Pull nvidia/cuda:12.6.3' | figlet -w 300 -f slant)\e[0m"
#echo ""

figlet_printf_green 'Pull nvidia/cuda:12.6.3'
docker pull nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04
#To verify nvidia docker isntallation and to check the underlying GPUs are leveraged , try running the following command

#printf "\e[32m$(echo -e 'verify with nvidia-smi commandr' | figlet -w 200 -f slant)\e[0m"

figlet_printf_green 'Verify with nvidia-smi commane'
docker run --rm --gpus all  nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04 nvidia-smi

figlet_printf_green 'Test nvidia-smi'
nvidia-smi
docker info | grep -i runtime
#sudo apt-get install -y nvidia-docker2

#printf "Restart docker after nvidia-docker2 installation" | figlet -w 300
figlet_printf_green 'Restart Docker'
echo "Running .....sudo systemctl restart docker"
sudo systemctl restart docker
sleep 10
figlet_printf_green 'Docker Restarted'
