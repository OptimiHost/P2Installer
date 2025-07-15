#!/usr/bin/env bash

PLAYER2_URL="https://github.com/Player2Linux/Player2/releases/latest/download/Player2-x86_64.AppImage"
PLAYER2_DEST="/usr/local/bin/Player2.AppImage"
LOG_FILE="/var/log/player2_installer.log"
UNINSTALL_SCRIPT="/usr/local/bin/p2uninstall"
MONITOR_SERVICE="/etc/systemd/system/p2monitor.service"

log() {
    local level="$1"
    local msg="$2"
    echo "[$level] $msg" >> "$LOG_FILE"
    case "$level" in
        INFO) echo -e "\033[1;34m[INFO]\033[0m $msg" ;;
        SUCCESS) echo -e "\033[1;32m[SUCCESS]\033[0m $msg" ;;
        WARNING) echo -e "\033[1;33m[WARNING]\033[0m $msg" ;;
        ERROR) echo -e "\033[1;31m[ERROR]\033[0m $msg" ;;
    esac
}

install_packages() {
    log INFO "Detecting distribution..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID=$ID
    else
        log ERROR "Unable to detect distribution."
        return 1
    fi

    log INFO "Installing packages for $DISTRO_ID..."
    case "$DISTRO_ID" in
        arch|manjaro) sudo pacman -Sy --noconfirm libva-utils ;;
        debian|ubuntu)
            sudo apt-get update
            sudo apt-get install -y libva-utils libegl1 libegl-mesa0 ;;
        fedora) sudo dnf install -y libva-utils mesa-libEGL ;;
        opensuse*|sles) sudo zypper install -y libva-utils Mesa-libEGL1 ;;
        gentoo)
            log WARNING "Gentoo detected. Please install libva-utils and mesa manually." ;;
        *) log WARNING "Unsupported distro. Please install required packages manually." ;;
    esac
}

install_player2() {
    log INFO "Downloading Player2..."
    if curl -L "$PLAYER2_URL" -o "$PLAYER2_DEST"; then
        chmod +x "$PLAYER2_DEST"
        log SUCCESS "Player2 installed at $PLAYER2_DEST"
    else
        log ERROR "Failed to download Player2."
        return 1
    fi
}

patch_webkit() {
    log INFO "Patching WebKit..."
    local shell_rc=""
    [[ -f ~/.bashrc ]] && shell_rc=~/.bashrc
    [[ -f ~/.zshrc ]] && shell_rc=~/.zshrc

    if [[ -n "$shell_rc" ]]; then
        if ! grep -q "WEBKIT_DISABLE_DMABUF_RENDERER=1" "$shell_rc"; then
            echo "export WEBKIT_DISABLE_DMABUF_RENDERER=1" >> "$shell_rc"
            log SUCCESS "Patched $shell_rc"
        else
            log INFO "Patch already exists in $shell_rc"
        fi
    else
        log WARNING "No shell config found to patch."
    fi
}

create_monitor_service() {
    log INFO "Creating monitor service..."
    sudo tee "$MONITOR_SERVICE" > /dev/null <<EOF
[Unit]
Description=Player2 Monitor Service
After=network.target

[Service]
ExecStart=/bin/bash -c 'tail -n0 -F /tmp/Player2.log | while read -r line; do echo "\$(date +%F_%T) [Player2 Warning] \$line" >> /var/log/Player2_Monitor.log; done'
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable --now p2monitor.service

    log SUCCESS "Monitor service created and started."
}

create_uninstall_script() {
    log INFO "Creating uninstaller..."

    sudo tee "$UNINSTALL_SCRIPT" > /dev/null <<'EOF'
#!/bin/bash
echo "Uninstalling Player2 and its patches..."
read -p "Are you sure? [y/N]: " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

echo "Removing Player2..."
sudo rm -f /usr/local/bin/Player2.AppImage

echo "Removing monitor service..."
sudo systemctl stop p2monitor.service
sudo systemctl disable p2monitor.service
sudo rm -f /etc/systemd/system/p2monitor.service
sudo systemctl daemon-reload

echo "Removing WebKit patch..."
sed -i '/WEBKIT_DISABLE_DMABUF_RENDERER=1/d' ~/.bashrc 2>/dev/null
sed -i '/WEBKIT_DISABLE_DMABUF_RENDERER=1/d' ~/.zshrc 2>/dev/null

echo "Player2 and all related components have been removed."
EOF

    sudo chmod +x "$UNINSTALL_SCRIPT"
    log SUCCESS "Uninstall script created at $UNINSTALL_SCRIPT"
}

main_menu() {
    while true; do
        CHOICE=$(dialog --clear --backtitle "Player2 Installer (Part 2)" \
            --title "Main Menu" \
            --menu "Choose an option:" 15 60 6 \
            1 "Install Player2" \
            2 "Install dependencies" \
            3 "Patch WebKit" \
            4 "Create service" \
            5 "Create uninstall script" \
            6 "Exit" \
            3>&1 1>&2 2>&3)

        clear
        case $CHOICE in
            1) install_player2 ;;
            2) install_packages ;;
            3) patch_webkit ;;
            4) create_monitor_service ;;
            5) create_uninstall_script ;;
            6) log INFO "Exiting..."; break ;;
        esac
    done
}

# === Start ===
touch "$LOG_FILE"
main_menu
