#!/bin/bash

#---Variables---
#Github address of the project
GIT="https://github.com/SkyMoonIndustries/SkyMenu.git"
#Project directory's path
DIR=/home/$USER
#Github cloning path
DOWN=/home/$USER/Downloads

#Cloning new version from repository
cd $DOWN
git clone $GIT

#Copying new files
sudo cp -r $DOWN/SkyMenu $DIR

#Removing cloned repository
cd $DOWN
rm -rf $DOWN/SkyMenu