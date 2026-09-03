#!/usr/bin/env sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
platformio_core=${PLATFORMIO_CORE_DIR:-"${HOME}/.platformio"}
download_dir=$(mktemp -d)
trap 'rm -rf "$download_dir"' EXIT HUP INT TERM

if [ "$(uname -s)" = "Darwin" ]; then
    toolchain_url="https://github.com/ambiot/ambd_arduino/raw/master/Arduino_package/release/ameba_d_toolchain_macos-1.0.1.tar.bz2"
    toolchain_hash="cc52c2c3650e21ef636bc10242432f75cd0f4884b1188f328982e77030d91787"
    toolchain_archive="ameba_d_toolchain_macos-1.0.1.tar.bz2"
    uploader_url="https://github.com/ambiot/ambd_arduino/raw/master/Arduino_package/release/ameba_d_tools_macos-1.1.3.tar.gz"
    uploader_hash="fec90f971a7f22b4e6ffbe770d25da4bd52cbd92cc8d473620d8b86ac1040713"
    uploader_archive="ameba_d_tools_macos-1.1.3.tar.gz"
    uploader_inner="ameba_d_tools_macos"
else
    toolchain_url="https://github.com/ambiot/ambd_arduino/raw/master/Arduino_package/release/ameba_d_toolchain_linux_64-1.0.1.tar.bz2"
    toolchain_hash="340ab2af5100102f7a1f5ba89b3490a843fa2aed05276427f5cc6c6c01032cd7"
    toolchain_archive="ameba_d_toolchain_linux_64-1.0.1.tar.bz2"
    uploader_url="https://github.com/ambiot/ambd_arduino/raw/master/Arduino_package/release/ameba_d_tools_linux-1.1.3.tar.gz"
    uploader_hash="f3cb543d63c59ba3d66f1181252cec407824d5cc196cf2fb1719aee4328c2c0e"
    uploader_archive="ameba_d_tools_linux-1.1.3.tar.gz"
    uploader_inner="ameba_d_tools_linux"
fi

verify_hash() {
    archive=$1
    expected=$2
    if command -v sha256sum >/dev/null 2>&1; then
        actual=$(sha256sum "$archive" | awk '{print $1}')
    else
        actual=$(shasum -a 256 "$archive" | awk '{print $1}')
    fi
    [ "$actual" = "$expected" ] || {
        echo "SHA-256 mismatch for $archive" >&2
        exit 1
    }
}

install_package() {
    name=$1
    url=$2
    expected_hash=$3
    archive_name=$4
    inner=$5
    manifest=$6
    archive_path="$download_dir/$archive_name"
    extract_path="$download_dir/$name-extract"
    destination="$platformio_core/packages/$name"

    echo "Downloading $name..."
    curl -fL "$url" -o "$archive_path"
    verify_hash "$archive_path" "$expected_hash"
    mkdir -p "$extract_path"
    tar --no-same-owner -xf "$archive_path" -C "$extract_path"
    rm -rf "$destination"
    mkdir -p "$destination"
    cp -R "$extract_path/$inner"/. "$destination"/
    cp "$project_root/$manifest" "$destination/package.json"
}

mkdir -p "$platformio_core/packages" "$platformio_core/platforms"

install_package \
    "framework-arduinorealtek-amebad" \
    "https://github.com/ambiot/ambd_arduino/raw/master/Arduino_package/release/ameba_d-3.1.9-build20250603.tar.gz" \
    "26740f342280f14645dd123a8c38bfd455e4b0f68a2bf2b325e7163d23c8fa90" \
    "ameba_d-3.1.9-build20250603.tar.gz" \
    "." \
    "support/package-manifests/framework.json"

install_package \
    "toolchain-realtek-amebad" \
    "$toolchain_url" \
    "$toolchain_hash" \
    "$toolchain_archive" \
    "asdk-6.5.0" \
    "support/package-manifests/toolchain.json"

install_package \
    "tool-realtek-amebad" \
    "$uploader_url" \
    "$uploader_hash" \
    "$uploader_archive" \
    "$uploader_inner" \
    "support/package-manifests/uploader.json"

platform_destination="$platformio_core/platforms/realtek-amebad"
rm -rf "$platform_destination"
cp -R "$project_root/platform" "$platform_destination"
chmod +x "$platform_destination"/../realtek-amebad/builder/main.py 2>/dev/null || true

echo
echo "BW16 support installed successfully."
echo "Open this project folder in VS Code, then click PlatformIO Build."
