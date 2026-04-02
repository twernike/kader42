mkdir -p /packages
mkdir -p /packages/base
pacman -Sw --cachedir=/packages/base --noconfirm base linux linux-firmware mkinitcpio sudo
cp -R /packages/base /run/archiso/airootfs