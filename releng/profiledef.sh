#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="Kader42"
# iso_label="kader42_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_label="kader42_mello"
iso_publisher="Thomas Wernike <https://kader42.de>"
iso_application="Kader⁴²"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="kader42"
buildmodes=('iso')
bootmodes=('uefi.systemd-boot')
pacman_conf="pacman.conf"
custom_repos=(
    "file:///packages"
)
airootfs_image_type="squashfs"
# airootfs_image_tool_options=('-comp' 'xz' '-Xbcj' 'x86' '-b' '1M' '-Xdict-size' '1M')

airootfs_image_tool_options=(
  '-comp' 'zstd'
  '-Xcompression-level' '5'
  '-processors' '4'
)


bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical' '--long' '-19')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/etc/sudoers.d/g_wheel"]="0:0:644"
  # ["/etc/polkit-1/rules.d/49-nopasswd_global.rules"]="0:0:644"
  ["/root"]="0:0:750"
  ["/root/.automated_script.sh"]="0:0:755"
  ["/root/customize_airootfs.sh"]="0:0:755"
  ["/root/.gnupg"]="0:0:700"
  ["/usr/local/bin/choose-mirror"]="0:0:755"
  ["/usr/local/bin/Installation_guide"]="0:0:755"
  ["/usr/local/bin/livecd-sound"]="0:0:755"
  ["/home/liveuser"]="1000:1000:700"
  ["/etc/mkinitcpio.conf"]="0:0:755"
)
users=(
  {
    "name": "liveuser",
    "password": '$1$AzoXqmKJ$r67GODY5j/K/GaXp2YZbY.',
    "groups": ["wheel", "audio", "video", "network", "input", "storage", "power", "lp"],
    "shell": "/bin/bash"
  }
)

