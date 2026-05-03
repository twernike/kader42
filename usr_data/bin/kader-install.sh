# sudo calamares
mkdir -p install_log
sudo calamares -d 2>&1 | tee install_log/calamares_debug.log