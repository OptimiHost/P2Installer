#!/usr/bin/env bash

# === Config ===
PLAYER2_APPIMAGE_URL="https://github.com/Player2Linux/Player2/releases/latest/download/Player2-x86_64.AppImage"
PLAYER2_DEST="/usr/local/bin/Player2.AppImage"
MONITOR_SERVICE_PATH="/etc/systemd/system/p2monitor.service"
UNINSTALL_SCRIPT="/usr/local/bin/p2uninstall"
LOG_FILE="/var/log/player2_installer.log"

# === Logging ===
log_info()  { echo -e "\033[1;32m[INFO]\033[0m $1" | tee -a "$LOG_FILE"; }
log_warn()  { echo -e "\033[1;33m[WARN]\033[0m $1" | tee -a "$LOG_FILE"; }
log_error() { echo -e "\033[1;31m[ERROR]\033[0m $1" | tee -a "$LOG_FILE"; }

# === Run Command Helper ===
run_command() {
    "$@" > >(while read -r line; do log_info "$line"; done) \
          2> >(while read -r line; do log_error "$line"; done)
}

# === Detect Distribution and Install System Packages ===
install_system_packages() {
    log_info "Installing system dependencies..."

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO_ID=$ID
    else
        log_error "Cannot detect distribution. Aborting."
        exit 1
    fi

    case "$DISTRO_ID" in
        arch | manjaro)
            run_command sudo pacman -Sy --noconfirm libva-utils
            ;;
        debian | ubuntu)
            run_command sudo apt-get update
            run_command sudo apt-get install -y libva-utils libegl1 libegl-mesa0
            ;;
        fedora)
            run_command sudo dnf install -y libva-utils mesa-libEGL
            ;;
        opensuse* | sles)
            run_command sudo zypper install -y libva-utils Mesa-libEGL1
            ;;
        gentoo)
            log_warn "Gentoo detected. Please ensure 'libva-utils' and 'mesa' are installed manually."
            ;;
        *)
            log_warn "Unsupported distro. Please install dependencies manually."
            ;;
    esac
}

# === Download and Install Player2 ===
install_player2() {
    log_info "Downloading Player2..."
    if curl -Lo "$PLAYER2_DEST" "$PLAYER2_APPIMAGE_URL"; then
        chmod +x "$PLAYER2_DEST"
        log_info "Player2 installed to $PLAYER2_DEST"
    else
        log_error "Failed to download Player2."
        exit 1
    fi
}

# === Apply WebKit Patch ===
apply_webkit_patch() {
    log_info "Applying WebKit patch..."

    SHELL_RC=""
    [[ -f ~/.zshrc ]] && SHELL_RC=~/.zshrc
    [[ -f ~/.bashrc ]] && SHELL_RC=~/.bashrc

    if [[ -n "$SHELL_RC" ]]; then
        if ! grep -q 'WEBKIT_DISABLE_DMABUF_RENDERER=1' "$SHELL_RC"; then
            echo 'export WEBKIT_DISABLE_DMABUF_RENDERER=1' >> "$SHELL_RC"
            log_info "Patched $SHELL_RC with WebKit fix."
        else
            log_info "WebKit patch already applied in $SHELL_RC."
        fi
    else
        log_warn "No known shell configuration file found to patch."
    fi
}

# === Set Up Monitoring Service ===
setup_monitor_service() {
    log_info "Setting up Player2 monitor service..."

    sudo tee "$MONITOR_SERVICE_PATH" > /dev/null <<EOF
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

    log_info "Monitor service started and enabled."
}

# === Create Uninstaller ===
create_uninstaller() {
    log_info "Creating uninstaller script at $UNINSTALL_SCRIPT..."

    sudo tee "$UNINSTALL_SCRIPT" > /dev/null <<'EOF'
#!/bin/bash

echo "Uninstalling Player2 and patches..."
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

echo "Player2 and associated files have been removed."
EOF

    sudo chmod +x "$UNINSTALL_SCRIPT"
    log_info "Uninstaller script ready. Use 'sudo p2uninstall' to remove Player2."
}

# === Main Installer Logic ===
main() {
    log_info "Starting Player2 installer..."

    install_system_packages
    install_player2
    apply_webkit_patch
    setup_monitor_service
    create_uninstaller

    log_info "Player2 installed successfully."
    log_info "Please restart your terminal or source your shell config to apply environment changes."
}

main "$@"

