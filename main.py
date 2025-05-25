import pprint as pp
import os
import sys
import time
import subprocess
import platform
import pwd
import shutil

# Variables
DISTRO = platform.freedesktop_os_release()
sudo_user = os.environ.get("SUDO_USER")
if not sudo_user:
    print("This script must be run with sudo privileges.")
    print("Please run the script again using: sudo python3 main.py")
    sys.exit(1)

home_dir = pwd.getpwnam(sudo_user).pw_dir
pretty_name = DISTRO.get("PRETTY_NAME", "Unknown Linux")
latest_ver_p2 = 'https://cdn.discordapp.com/attachments/1247544452294377547/1369692197229694986/Player2_0.10.3_amd64.AppImage?ex=682e9503&is=682d4383&hm=93a963ec279cc65e8dfd89981d7c1b17f382311e046ba57bb27619208f835e10&'
appimage_filename = os.path.basename(latest_ver_p2)
appimage_path = os.path.join(home_dir, 'player2', 'Player2.AppImage')
YELLOW = "\033[93m"
RESET = "\033[0m"
BANNER = "\033[91m"
GREEN = "\033[92m"


# functions
def check_sudo():
    if os.geteuid() != 0:
        red("This script must be run with sudo privileges.")
        red("Please run the script again using: sudo python3 main.py")
        sys.exit(1)

def install_p2():
    print(f"{YELLOW}*** Downloading Player2{RESET}")
    os.makedirs(f'{home_dir}/player2', exist_ok=True)
    download_path = os.path.join(home_dir, 'player2', 'Player2.AppImage')
    subprocess.run(['wget', latest_ver_p2, '-O', download_path])
    subprocess.run(['chmod', '+x', download_path])

def patches():
    home = os.path.expanduser("~")
    env_line = "export WEBKIT_DISABLE_DMABUF_RENDERER=1\n"

    shells = {
        "bash": os.path.join(home, ".bashrc"),
        "zsh": os.path.join(home, ".zshrc"),
    }

    installed_shells = [shell for shell in shells if shutil.which(shell)]

    if not installed_shells:
        red("No bash or zsh shell found on this system.")
        exit('Shells were not found')

    for shell in installed_shells:
        rc_path = shells[shell]
        if not os.path.exists(rc_path):
            open(rc_path, "w").close()

        with open(rc_path, "r") as f:
            lines = f.readlines()

        if any(env_line.strip() == line.strip() for line in lines):
            print(f"{env_line.strip()} already set in {rc_path}")
        else:
            with open(rc_path, "a") as f:
                f.write("\n# Added by installer\n")
                f.write(env_line)
            print(f"Added {env_line.strip()} to {rc_path}")

def yellow(msg):
    print(f"{YELLOW}{msg}{RESET}")

def red(msg):
    print(f"{BANNER}{msg}{RESET}")

def green(msg):
    print(f"{GREEN}{msg}{RESET}")
    
# Check for sudo privileges before proceeding
check_sudo()

red(r'''
  Optimi's   _____           _        _ _           
 |  __ \__ \|_   _|         | |      | | |          
 | |__) | ) | | |  _ __  ___| |_ __ _| | | ___ _ __ 
 |  ___/ / /  | | | '_ \/ __| __/ _` | | |/ _ \ '__|
 | |    / /_ _| |_| | | \__ \ || (_| | | |  __/ |   
 |_|   |____|_____|_| |_|___/\__\__,_|_|_|\___|_|   
                                           Version 1.0DEV         
''')
print(" *** Searching for OS you are using... ***")

# OS detection and package installation
if pretty_name == "Arch Linux":
    yellow("*** You're using Arch Linux")
    yellow("*** Installing packages")
    subprocess.run(['sudo', 'pacman', '-S', '--needed',
                    'webkit2gtk-4.1', 'base-devel', 'curl', 'wget',
                    'file', 'openssl', 'appmenu-gtk-module',
                    'libappindicator-gtk3', 'librsvg'])
    install_p2()
    yellow('*** Setting up patches')
    patches()

elif any(name in pretty_name for name in ["Ubuntu", "Debian", "Pop!_OS"]):
    yellow("*** You're using Ubuntu based OS")
    yellow("*** Installing packages")
    subprocess.run(['sudo', 'apt', 'install', '-y',
                    'libwebkit2gtk-4.1-dev', 'build-essential', 'curl', 'wget', 'file',
                    'libxdo-dev', 'libssl-dev', 'libayatana-appindicator3-dev', 'librsvg2-dev'])
    install_p2()
    yellow('*** Setting up patches')
    patches()

elif "Fedora" in pretty_name:
    yellow("*** You're using Fedora")
    yellow("*** Installing packages")
    subprocess.run(['sudo', 'dnf', 'install', '-y',
                    'webkit2gtk4.1-devel', 'openssl-devel', 'curl', 'wget', 'file',
                    'libappindicator-gtk3-devel', 'librsvg2-devel'])
    subprocess.run(['sudo', 'dnf', 'group', 'install', '-y', 'c-development'])
    install_p2()
    yellow('*** Setting up patches')
    patches()

elif "Gentoo" in pretty_name:
    yellow("*** You're using Gentoo")
    yellow("*** Installing packages")
    subprocess.run(['sudo', 'emerge', '--ask',
                    'net-libs/webkit-gtk:4.1', 'dev-libs/libappindicator',
                    'net-misc/curl', 'net-misc/wget', 'sys-apps/file'])
    install_p2()
    yellow('*** Setting up patches')
    patches()

elif "openSUSE" in pretty_name:
    yellow("*** You're using openSUSE")
    yellow("*** Installing packages")
    subprocess.run(['sudo', 'zypper', 'in', '-y',
                    'webkit2gtk3-devel', 'libopenssl-devel', 'curl', 'wget', 'file',
                    'libappindicator3-1', 'librsvg-devel'])
    subprocess.run(['sudo', 'zypper', 'in', '-t', 'pattern', 'devel_basis'])
    install_p2()
    yellow('*** Setting up patches')
    patches()

elif "Alpine" in pretty_name:
    yellow("*** You're using Alpine")
    yellow("*** Installing packages")
    subprocess.run(['sudo', 'apk', 'add',
                    'build-base', 'webkit2gtk', 'curl', 'wget', 'file',
                    'openssl', 'libayatana-appindicator-dev', 'librsvg'])
    install_p2()
    yellow('*** Setting up patches')
    patches()

else:
    red("Unknown Linux distro")
    red("Please make an issue on https://github.com/OptimiDEV/P2Installer/issues")

print(f"\nDone!")
print(f"You can now run Player2 using {appimage_path}")
print("Thanks for using Optimi's P2Installer!")
