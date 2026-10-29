#!/usr/bin/env bash
set -euo pipefail

# Configuration
PKGNAME="kader42-convertible-tools"
PKGVER="2.0.0"
PKGREL="3"
PKGDESC="An event listener and a launcher switcher that ensures you have the Dash menu in tablet mode and the standard Start menu in laptop mode."
MAINTAINER="Thomas Wernike <support@kader42.de>"

TARGET_DIRS=("etc" "usr")

# Arrays vorbereiten
source_entries=()
sha256_entries=()
install_lines=()

pkg_path=$(pwd)

    # build listener
    cd rust/kader42-tablet-event-listener/
    cargo build --release --locked
    cd target/release
    mv -f "kader42-tablet-event-listener" "$pkg_path/usr/bin"
    cd $pkg_path

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

echo "==> PKGBUILD successful!"
echo "Now, build package..."
makepkg -s
echo "Move the package to the repo.db directory..."
mv -f *.pkg.tar.zst ..
cd ..
repo-add kader42.db.tar.gz *.pkg.tar.zst