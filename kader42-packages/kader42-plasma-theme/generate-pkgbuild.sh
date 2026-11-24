#!/usr/bin/env bash
set -euo pipefail

# Configuration
PKGNAME="kader42-plasma-theme"
PKGVER="1.0.6"
PKGREL="5"
PKGDESC="The specific Kader42 Plasma Theme"
MAINTAINER="Thomas Wernike <support@kader42.de>"

TARGET_DIRS=("etc" "usr")

# Arrays vorbereiten
source_entries=()
sha256_entries=()
install_lines=()


# 2. Ordner etc/ und usr/ scannen
for dir in "${TARGET_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        while IFS= read -r -d '' file; do
            if [ -f "$file" ]; then
                # Select mode: 755 for executables / usr/bin, otherwise 644
                if [[ "$file" == usr/bin/* ]] || [ -x "$file" ]; then
                    install_lines+=("    install -Dm755 \"\${startdir}/$file\" \"\${pkgdir}/$file\"")
                else
                    install_lines+=("    install -Dm644 \"\${startdir}/$file\" \"\${pkgdir}/$file\"")
                fi
            fi
        done < <(find "$dir" -type f -print0 | sort -z)
    fi
done

# 3. Generate and write the PKGBUILD directly
cat <<EOF > PKGBUILD
# Maintainer: ${MAINTAINER}
pkgname=${PKGNAME}
pkgver=${PKGVER}
pkgrel=${PKGREL}
pkgdesc="${PKGDESC}"
arch=('any')
depends=('kader42-wallpapers')
install=${PKGNAME}.install

source=(
$(printf "%s\n" "${source_entries[@]}")
)

sha256sums=(
$(printf "%s\n" "${sha256_entries[@]}")
)


package() {
$(printf "%s\n" "${install_lines[@]}")

}
EOF

echo "==> PKGBUILD has been successfully updated!"
makepkg -s
mv *.pkg.tar.zst ../
cd ..
repo-add kader42.db.tar.gz *.pkg.tar.zst