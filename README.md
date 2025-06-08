---

# 🎮 Optimi's P2Installer

**Run Player2 (from [player2.game](https://player2.game)) on Linux with ease.**
Optimi's P2Installer is a cross-distro Python installer that automates the setup of dependencies, environment variables, and the latest Player2.AppImage.

---

## 🤖 What is Player2?

**Player2** (available at [player2.game](https://player2.game)) is an AI-powered platform designed to enhance gaming experiences by providing intelligent in-game assistance. It enables gamers to:

* **Integrate AI companions** into games like Minecraft, offering dynamic interactions and support.
* **Access AI APIs** for indie game developers to create custom AI-driven content.
* **Explore and share AI mods and games**, fostering a community of creators and players .

---

## ✅ P2Installer Features

* **Cross-distro support**: Works on Arch Linux, Ubuntu/Debian, Fedora, Gentoo, openSUSE, and Alpine Linux.
* **Automated setup**: Installs necessary dependencies, patches, and downloads the latest Player2.AppImage.

---

## ⚙️ Requirements

* Linux (any major distro)
* `sudo` privileges
* Python 3.6 or later

---

## 🚀 Installation

Run the following command to install Player2:

```bash
curl -fsSL https://raw.githubusercontent.com/OptimiDEV/P2Installer/main/main.py | sudo python3
```

This script will:

1. Detect your Linux distribution.
2. Install required dependencies.
3. Download the latest Player2.AppImage.
4. Make the AppImage executable.
5. Patch your shell environment variables.

---

## 🛠 Behind the Scenes

The installer script performs the following steps:

1. **Check for sudo privileges**: Ensures the script is run with appropriate permissions.
2. **Display ASCII banner**: Shows a welcome message with the Optimi logo.
3. **Detect operating system**: Identifies the Linux distribution using `platform.freedesktop_os_release()`.
4. **Install dependencies**: Based on the detected OS, installs necessary packages using the appropriate package manager.
5. **Download Player2.AppImage**: Fetches the latest version of the Player2 AppImage from the official source.
6. **Set executable permissions**: Makes the downloaded AppImage executable.
7. **Patch shell environment**: Adds the necessary environment variable to `.bashrc` or `.zshrc` to ensure proper functionality.

---

## 🛡️ Notes & Cleanup

* **Uninstallation**: To remove Player2, delete the `~/player2/Player2.AppImage` file and remove the `export WEBKIT_DISABLE_DMABUF_RENDERER=1` line from your shell configuration file.
* **Manual Updates**: The installer does not handle updates. To update Player2, re-run the installation script or manually download the latest AppImage.

