#!/usr/bin/env bash
set -euo pipefail

# Configuration
PKGNAME="kader42-core"
PKGVER="1.0.12"
PKGREL="4"
PKGDESC="Core configurations and systemd units for Kader42"
MAINTAINER="Thomas Wernike <support@kader42.de>"

TARGET_DIRS=("etc" "usr")

# Arrays vorbereiten
source_entries=()
sha256_entries=()
install_lines=()

# 1. Lose Basis-Dateien hinzufügen
base_sources=(
    'kader42-cleanup.service'
    'kader42-software-center-favorite.upd'
    'kader42-software-center-favorite.js'
)

for src in "${base_sources[@]}"; do
    source_entries+=("    '$src'")
    sha256_entries+=("    'SKIP'")
done

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
install=${PKGNAME}.install

source=(
$(printf "%s\n" "${source_entries[@]}")
)

sha256sums=(
$(printf "%s\n" "${sha256_entries[@]}")
)

conflicts=('kader42-hooks')
replaces=('kader42-hooks')

package() {
$(printf "%s\n" "${install_lines[@]}")

    # Spezielle Services & KConf-Symlinks
    install -Dm644 "\${srcdir}/kader42-cleanup.service" "\${pkgdir}/usr/lib/systemd/system/kader42-cleanup.service"
    mkdir -p "\${pkgdir}/usr/lib/systemd/system/multi-user.target.wants"
    ln -sf "../kader42-cleanup.service" "\${pkgdir}/usr/lib/systemd/system/multi-user.target.wants/kader42-cleanup.service"

    install -Dm644 "\${srcdir}/kader42-software-center-favorite.upd" "\${pkgdir}/usr/share/kconf_update/kader42-software-center-favorite.upd"
    install -Dm755 "\${srcdir}/kader42-software-center-favorite.js" "\${pkgdir}/usr/share/kconf_update/kader42-software-center-favorite.js"
}
EOF

echo "==> PKGBUILD wurde erfolgreich aktualisiert!"