#!/bin/bash

# Function to display text with figlet in red
figlet_print_red() {
    printf "\e[31m$(figlet -w 200 "$1")\e[0m\n"
}

# Get the current working directory
CURRENT_DIR=$(pwd)

# Append the expected Git repository directory
REPO_DIR="$CURRENT_DIR/shop-talk"

# Check if figlet is installed
if ! dpkg -l | grep -q figlet; then
    sudo apt update
    sudo apt install -y figlet
else
    echo "Figlet is already installed."
fi

# Clone the repository if it doesn't already exist
if [ ! -d "$REPO_DIR" ]; then
    echo -e $'\e[1;32mCloning GIT Repository. Press Enter to Proceed...\e[0m'
    read -r
    figlet_print_red "Cloning Git Repo"
    git clone git@github.com:sagarsGitArena/shop-talk.git
    #git clone --branch backup-2025-03-16 git@github.com:sagarsGitArena/shop-talk.git
    cd shop-talk
    git fetch origin
    echo -e $'\e[1;32mRunning git checkout backup-2025-03-16 . Press Enter to Proceed....\e[0m'
    read -r
    #git checkout backup-2025-03-16
    git checkout -b backup-2025-03-16 origin/backup-2025-03-16

else
    figlet_print_red "Git Repo Already Cloned"
fi


echo "Press Enter to proceed..."
read -r -p "Setup is ready. Press Enter to proceed..." 

# List the current directory's content
#
PWD=`pwd`



echo "Listing contents of the current directory: $PWD"
echo "-------------------------------------------"

# List files and directories
ls -lah

echo "-------------------------------------------"
echo -e  $'\e[1;32mPress Enter to proceed...\e[0m'
read -r 


# Check if the repository directory exists
if [ -d "$REPO_DIR" ]; then
    echo "Directory exists: $REPO_DIR"
    cd "$REPO_DIR" || exit 1
    echo "Running .... [git pull]"
    git pull
    sh set-up/set-up-env.sh
else
    echo "Directory does not exist: $REPO_DIR"
fi
