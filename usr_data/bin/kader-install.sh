#!/bin/bash

echo "************************************************************"
echo " Kader⁴² Installer"
echo "************************************************************"

# We check whether ‘not found’ appears in the ldd output of Calamares. 
# If it does, we will print the missing libraries and exit with an error message. 
# If all libraries are found, we will start Calamares as usual.

MISSING_LIBS=$(ldd /usr/bin/calamares | grep "not found")

echo "[Kader⁴² Installer] Checking for missing libraries in Calamares..."
if [ -z "$MISSING_LIBS" ]; then
    echo "[Kader⁴² Installer]✅ All libraries loaded. Start Calamares..."
else
    echo "[Kader⁴² Installer]⛔ Missing libraries detected❗⚠️" 
    echo "$MISSING_LIBS"
    echo "[Kader⁴² Installer] Please try running ‘pacman -Syu’ in the live system.
    If you are the administrator or user of this system, please ensure all required libraries are installed.
    If all requirements are met, you can contact support@kader42.de. Thank you for your understanding."
    exit 1
fi

# Start von Calamares
sudo calamares #--config /etc/calamares/settings.conf -d