#!/usr/bin/env bash
set -euo pipefail

# Configuration
PKGNAME="kader42-plymouth-themes"
PKGVER="1.0.0"
PKGREL="4"
PKGDESC="Plymouth themes for Kader42"
MAINTAINER="Thomas Wernike <support@kader42.de>"

TARGET_DIRS=("usr")

# Arrays vorbereiten
sha256_entries=()
install_lines=()

# 2. Ordner etc/ und usr/ scannen
for dir in "${TARGET_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        while IFS= read -r -d '' file; do
            if [ -f "$file" ]; then
                # source_entries+=("    '$file'")
                # sha256_entries+=("    'SKIP'")

                # Modus wählen: 755 für Executables / usr/bin, sonst 644
                if [[ "$file" == usr/bin/* ]] || [ -x "$file" ]; then
                    install_lines+=("    install -Dm755 \"\${startdir}/$file\" \"\${pkgdir}/$file\"")
                else
                    install_lines+=("    install -Dm644 \"\${startdir}/$file\" \"\${pkgdir}/$file\"")
                fi
            fi
        done < <(find "$dir" -type f -print0 | sort -z)
    fi
done

# 3. PKGBUILD direkt generieren und schreiben
cat <<EOF > PKGBUILD
# Maintainer: ${MAINTAINER}
pkgname=${PKGNAME}
pkgver=${PKGVER}
pkgrel=${PKGREL}
pkgdesc="${PKGDESC}"
arch=('any')
depends=('bash' 'dbus' 'kernel-modules-hook' 'pacback' 'systemd-boot-pacman-hook' 'system-config-printer' 'cups' 'libreoffice-fresh-de' 'kader42-software-center' 'kader42-plasma-theme')

package() {
$(printf "%s\n" "${install_lines[@]}")

}
EOF

echo "==> PKGBUILD generated successful!"
echo "Generate package"
makepkg -s