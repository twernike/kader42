#!/bin/bash
echo Please enter your sudo password if you are prompted to do so.
echo Testing...
sudo plymouthd
sudo plymouth --show-splash
sleep 10
sudo plymouth quit
echo Done!
echo Have a nice day!