if ! dpkg -l | grep -q figlet; then
    sudo apt update
    sudo apt install -y figlet
else
    echo "Figlet is already installed."
fi

#printf 'Clone git repository' | figlet -w 200
#git clone git@github.com:sagarsGitArena/shop-talk.git

printf "\e[31m$(figlet -w 200 Clone git repo )\e[0m"

curl -s https://raw.githubusercontent.com/sagarsGitArena/shop-talk/main/clone-git-repo.sh | bash

if [ -d “shop-talk ]; then
    echo "Directory exists"
	 cd short-talk
	 sh set-up/set-up-env.sh
else
    echo "Directory does not exist"
fi


