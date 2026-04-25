#!/usr/bin/env python3
import os
import sys
import hashlib
import subprocess
import shutil
import re
from pathlib import Path

# THE ANTHEROS CORE SCRIPT (Infused)
ANTHER_CUSTOMIZE_SCRIPT = r"""#!/bin/bash
# Enable 32-bit architecture for Gaming
dpkg --add-architecture i386
apt update && apt upgrade -y

# Branding: os-release
cat <<EOF > /etc/os-release
NAME="AntherOS"
VERSION="24.04 LTS"
ID=antheros
ID_LIKE="ubuntu debian"
PRETTY_NAME="AntherOS 24.04 LTS"
VERSION_ID="24.04"
HOME_URL="https://antheros.in"
SUPPORT_URL="https://antheros.in/support"
BUG_REPORT_URL="https://antheros.in/issues"
PRIVACY_POLICY_URL="https://antheros.in/privacy"
VERSION_CODENAME=noble
UBUNTU_CODENAME=noble
LOGO=distributor-logo-antheros-os
EOF

# Branding: lsb-release
cat <<EOF > /etc/lsb-release
DISTRIB_ID=AntherOS
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="AntherOS 24.04 LTS Gaming Edition"
EOF

# Define and install package stack
PACKAGES="sl cmatrix cheese steam lutris gamemode mangohud goverlay vulkan-tools vlc btop neofetch timeshift libgl1-mesa-dri:i386 libgl1-mesa-glx:i386 libvulkan1:i386 plymouth plymouth-themes initramfs-tools openjdk-21-jdk unzip wget"

apt install -y $PACKAGES

# Wallpaper Injection
wget -O /tmp/wallpaper.zip https://github.com/antheros-technologies/AntherOS-Core/raw/refs/heads/main/wallpaper.zip
rm -rf /usr/share/backgrounds/cosmic/*
unzip /tmp/wallpaper.zip -d /usr/share/backgrounds/cosmic/

# Plymouth Theme Injection
wget -O /tmp/Anther-Default-Plymouth.zip https://github.com/anagh9090/Anther-Default-Plymouth/releases/download/1.0.0/Anther-Default-Plymouth.zip
unzip /tmp/Anther-Default-Plymouth.zip -d /usr/share/plymouth/themes/
update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/anther-default/anther-default.plymouth 100
plymouth-set-default-theme anther-default
update-initramfs -u

echo "AntherOS Core Customization Complete."
"""

class AntherICLI:
    ISO_URL = "https://iso.pop-os.org/24.04/amd64/generic/24/pop-os_24.04_amd64_generic_24.iso"
    EXPECTED_HASH = "813f14421c09320fa21e8cd32832c3ac64b46918ad88e76aba983f691a343f29"
    
    BASE_DIR = Path(__file__).parent.absolute()
    ISO_PATH = BASE_DIR / "pop-os_24.04.iso"
    WORK_DIR = BASE_DIR / "anther_work"
    EXTRACT_ISO = WORK_DIR / "iso_content"
    SQUASH_ROOT = WORK_DIR / "squashfs-root"

    def __init__(self):
        if os.geteuid() != 0:
            print("\033[91m[ERROR]\033[0m Run with: sudo python3 main.py")
            sys.exit(1)
        print("\033[94m" + "="*60 + "\n   ANTHEROS INFUSED BUILDER (ICLI) - BOOTABLE FIXED\n" + "="*60 + "\033[0m")

    def try_command(self, cmd):
        subprocess.run(cmd, check=True)

    def verify_base(self):
        print("\n\033[96m[1/4] Verifying Base ISO\033[0m")
        if self.ISO_PATH.exists():
            h = hashlib.sha256()
            with open(self.ISO_PATH, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""): h.update(chunk)
            if h.hexdigest() == self.EXPECTED_HASH:
                print("\033[92m✔ Verified.\033[0m")
                return
        print(f"Downloading Base ISO...")
        self.try_command(["wget", "-O", str(self.ISO_PATH), self.ISO_URL])

    def unpack(self):
        print("\n\033[96m[2/4] Unpacking Environment\033[0m")
        if self.WORK_DIR.exists(): shutil.rmtree(self.WORK_DIR)
        self.EXTRACT_ISO.mkdir(parents=True)
        self.try_command(["7z", "x", str(self.ISO_PATH), f"-o{self.EXTRACT_ISO}", "-y"])
        
        squash_files = list(self.EXTRACT_ISO.rglob("*.squashfs"))
        if not squash_files: sys.exit("No squashfs found!")
        self.target_squash = squash_files[0]
        
        print("--> Unsquashing (Extracting Filesystem)...")
        self.try_command(["unsquashfs", "-f", "-d", str(self.SQUASH_ROOT), str(self.target_squash)])

    def run_infused_script(self):
        print("\n\033[96m[3/4] Running Infused Customization\033[0m")
        target_path = self.SQUASH_ROOT / "tmp" / "infused_customize.sh"
        
        with open(target_path, "w") as f:
            f.write(ANTHER_CUSTOMIZE_SCRIPT)
        target_path.chmod(0o755)

        try:
            for mnt in ["dev", "proc", "sys"]:
                self.try_command(["mount", "--bind", f"/{mnt}", str(self.SQUASH_ROOT / mnt)])
            shutil.copy("/etc/resolv.conf", str(self.SQUASH_ROOT / "etc/resolv.conf"))

            subprocess.run(["chroot", str(self.SQUASH_ROOT), "/bin/bash", "/tmp/infused_customize.sh"], check=True)
        
        finally:
            for mnt in ["sys", "proc", "dev"]:
                subprocess.run(["umount", "-l", str(self.SQUASH_ROOT / mnt)], stderr=subprocess.DEVNULL)
            if target_path.exists(): target_path.unlink()

    def pack(self):
        print("\n\033[96m[4/4] Packing AntherOS ISO\033[0m")
        if self.target_squash.exists(): self.target_squash.unlink()

        print("--> Squashing (XZ Compression)...")
        self.try_command(["mksquashfs", str(self.SQUASH_ROOT), str(self.target_squash), "-comp", "xz", "-noappend"])

        print("--> Detecting Boot Images...")
        # Dynamically find boot files in case they moved
        isolinux_bin = next(self.EXTRACT_ISO.rglob("isolinux.bin"), None)
        efi_img = next(self.EXTRACT_ISO.rglob("efi.img"), None)
        
        if not isolinux_bin or not efi_img:
            print("\033[91m[WARNING]\033[0m Boot files missing in ISO structure. ISO might not be bootable.")

        output_iso = self.BASE_DIR / "AntherOS-24.04-Infused.iso"
        
        # Professional bootable xorriso flags
        xorriso_cmd = [
            "xorriso", "-as", "mkisofs",
            "-r", "-V", "AntherOS_24_04",
            "-o", str(output_iso),
            "-J", "-joliet-long",
            "-b", str(isolinux_bin.relative_to(self.EXTRACT_ISO)) if isolinux_bin else "isolinux/isolinux.bin",
            "-c", "isolinux/boot.cat",
            "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table",
            "-eltorito-alt-boot",
            "-e", str(efi_img.relative_to(self.EXTRACT_ISO)) if efi_img else "boot/grub/efi.img",
            "-no-emul-boot", "-isohybrid-gpt-basdat",
            str(self.EXTRACT_ISO)
        ]

        print(f"--> Generating Bootable Hybrid ISO...")
        self.try_command(xorriso_cmd)
        
        # Return ownership
        real_user = os.environ.get('SUDO_USER')
        if real_user:
            self.try_command(["chown", f"{real_user}:{real_user}", str(output_iso)])

        print(f"\n\033[92m[SUCCESS] Build Complete: {output_iso.name}\033[0m")

    def run(self):
        self.verify_base()
        self.unpack()
        self.run_infused_script()
        input("\nEnvironment Ready. Press [ENTER] to pack the final ISO...")
        self.pack()

if __name__ == "__main__":
    try:
        AntherICLI().run()
    except KeyboardInterrupt:
        print("\nStopped.")
