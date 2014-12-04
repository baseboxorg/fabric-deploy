#!/usr/bin/env bash

# exit if there are errors
set -e
	
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

#update homebrew and install vagrant
brew doctor
brew update
brew tap phinze/homebrew-cask && brew install brew-cask
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bash_profile
brew install node
npm install -g bower grunt-cli
sudo gem install foundation
brew cask install virtualbox
brew cask install vagrant
curl -o /tmp/vbox.vbox-extpack http://download.virtualbox.org/virtualbox/4.3.18/Oracle_VM_VirtualBox_Extension_Pack-4.3.18-96516.vbox-extpack
VBoxManage extpack install /tmp/vbox.vbox-extpack


# Not working right now
#--------------------------

# read -p "Download and install the custom Vagrant Box? [yn]" box
# if [[ $box = y ]] ; then
# 	curl -o /tmp/package.box http://downloads.dontworryabout.us/package.box
# 	vagrant box add project /tmp/package.box
# fi

#--------------------------


# install pip to set up frontend management
echo "Installing Pip"
sudo easy_install pip
echo "Installing Python Dependencies"
sudo pip install -r requirements.txt
	
