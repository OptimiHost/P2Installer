#!/usr/bin/env python3
"""
Player2 Linux Patches Console UI Installer
(C) Alex Mueller - OptimiDEV
"""

import curses
import logging
import os
import sys
import subprocess
import platform
import pwd
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime

class Player2ConsoleInstaller:
    def __init__(self):
        self.sudo_user = os.environ.get('SUDO_USER')
        # Setup logging
        self.setup_logging()
        # Check sudo privileges first
        if not self.check_sudo():
            self.logger.error("This installer must be run with sudo privileges.")
            print("This installer must be run with sudo privileges.")
            print("Please run: bash -c 'curl -fsSL https://raw.githubusercontent.com/OptimiDEV/P2Installer/main/main.py -o /tmp/p2installer.py && sudo python3 /tmp/p2installer.py'")
            sys.exit(1)

        
        self.distros = ["Arch-based(Like EndeavourOS)","Fedora-based(Like Endeavour)", "Debian(Like Zorin or Ubuntu)"]
        self.pretty_name = "UwUntu"

        if self.sudo_user:
            self.home_dir = pwd.getpwnam(self.sudo_user).pw_dir
        else:
            self.home_dir = os.path.expanduser("~")
        self.latest_ver_p2 = 'https://downloadclient.player2.game/linux/player2.AppImage'
        self.appimage_path = os.path.join(self.home_dir, 'player2', 'Player2.AppImage')
        
        # Installation options
        self.install_monitor = False
        self.install_patches = True
        
        # Start curses
        try:
            curses.wrapper(self.main)
        except Exception as e:
            print(f"Error running installer: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = os.path.expanduser("~/p2installer_logs")
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"p2installer_{timestamp}.log")
        
        self.logger = logging.getLogger('P2Installer')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def check_sudo(self):
        return os.geteuid() == 0
    
    def main(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        
        # Initialize colors if supported
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Title
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Highlight
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Success
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
            curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Info
            curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal
        
        # Show screens in sequence
        if self.show_intro_screen():
            if self.show_distro_selection_screen():
                if self.show_addons_screen():
                    self.show_installation_screen()

        
        # Wait for final key press
        self.stdscr.addstr(self.stdscr.getmaxyx()[0] - 1, 0, "Press any key to exit...")
        self.stdscr.refresh()
        self.stdscr.getch()
    
    def get_color(self, pair_num):
        """Get color pair, fallback to normal if colors not supported"""
        if curses.has_colors():
            return curses.color_pair(pair_num)
        return curses.A_NORMAL
    
    def draw_box(self, y, x, height, width, title=""):
        """Draw a box with optional title"""
        try:
            # Ensure we don't draw outside screen bounds
            max_y, max_x = self.stdscr.getmaxyx()
            if y + height >= max_y or x + width >= max_x:
                return
                
            # Draw box border
            for i in range(height):
                for j in range(width):
                    draw_y, draw_x = y + i, x + j
                    if draw_y >= max_y or draw_x >= max_x:
                        continue
                        
                    if i == 0 or i == height - 1:
                        if j == 0 or j == width - 1:
                            self.stdscr.addch(draw_y, draw_x, '+')
                        else:
                            self.stdscr.addch(draw_y, draw_x, '-')
                    elif j == 0 or j == width - 1:
                        self.stdscr.addch(draw_y, draw_x, '|')
            
            # Add title if provided
            if title:
                title_text = f"[ {title} ]"
                title_x = x + (width - len(title_text)) // 2
                if title_x >= 0 and y >= 0 and title_x + len(title_text) < max_x:
                    self.stdscr.addstr(y, title_x, title_text, self.get_color(1))
        except curses.error:
            pass  # Ignore drawing errors
    
    def safe_addstr(self, y, x, text, attr=None):
        """Safely add string to screen"""
        try:
            max_y, max_x = self.stdscr.getmaxyx()
            if y >= max_y or x >= max_x:
                return
            
            # Truncate text if it would exceed screen width
            available_width = max_x - x - 1
            if len(text) > available_width:
                text = text[:available_width]
            
            if attr:
                self.stdscr.addstr(y, x, text, attr)
            else:
                self.stdscr.addstr(y, x, text)
        except curses.error:
            pass  # Ignore drawing errors
    
    def show_intro_screen(self):
        """Show introduction screen"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Ensure minimum screen size
        if h < 20 or w < 60:
            self.safe_addstr(0, 0, "Terminal too small. Please resize to at least 60x20.")
            self.stdscr.refresh()
            self.stdscr.getch()
            return False
        
        # Draw main box
        box_width = min(70, w - 4)
        box_height = min(20, h - 4)
        box_x = (w - box_width) // 2
        box_y = (h - box_height) // 2
        
        self.draw_box(box_y, box_x, box_height, box_width, "P2Patches Installer")
        
        # ASCII Art Logo
        logo = [
            " _____ ___  _____           _        _ _           ",
            "|  __ \\__ \\|_   _|         | |      | | |          ",
            "| |__) | ) | | |  _ __  ___| |_ __ _| | | ___ _ __ ",
            "|  ___/ / /  | | | '_ \\/ __| __/ _` | | |/ _ \\ '__|",
            "| |    / /_ _| |_| | | \\__ \\ || (_| | | |  __/ |   ",
            "|_|   |____|_____|_| |_|___/\\__\\__,_|_|_|\\___|_|   ",
            "                                                    ",
            "                                                    "
        ]
        
        # Display logo if it fits
        logo_y = box_y + 2
        if box_width >= 40:
            for i, line in enumerate(logo):
                if logo_y + i < box_y + box_height - 8:
                    logo_x = box_x + (box_width - len(line)) // 2
                    self.safe_addstr(logo_y + i, logo_x, line, self.get_color(2))

        # Version and info
        info_y = logo_y + len(logo) + 1
        info_lines = [
            "P2Installer Script v3.1",
            "Requires Root Access",
            "",
            "This script patches and installes Player2 on Linux.",
            f"Detected OS: {self.pretty_name[:30]}...",
            "Estimated time: 5s",
            "Press ENTER to continue or 'q' to quit",
            ""
        ]
        
        for i, line in enumerate(info_lines):
            if info_y + i < box_y + box_height - 2:
                line_x = box_x + (box_width - len(line)) // 2
                color = self.get_color(5) if i < 2 else self.get_color(6)
                self.safe_addstr(info_y + i, line_x, line, color)
        
        self.stdscr.refresh()
        
        # Wait for input
        while True:
            key = self.stdscr.getch()
            if key == ord('\n') or key == ord('\r') or key == 10:
                return True
            elif key == ord('q') or key == ord('Q'):
                return False
                
    def show_distro_selection_screen(self):
        """Prompt user to select their distro manually"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
    
        # Define distro choices
        distros = [
            "Arch Linux / Manjaro",
            "Debian / Ubuntu",
            "Fedora",
            "openSUSE",
            "Other (Generic)"
        ]
        selected = 0
    
        box_width = min(70, w - 4)
        box_height = min(len(distros) + 8, h - 4)
        box_x = (w - box_width) // 2
        box_y = (h - box_height) // 2
    
        while True:
            self.stdscr.clear()
            self.draw_box(box_y, box_x, box_height, box_width, "Select Your Linux Distro")
    
            self.safe_addstr(box_y + 2, box_x + 4, "Use UP/DOWN arrows to select your distro.", self.get_color(6))
            self.safe_addstr(box_y + 3, box_x + 4, "Press ENTER to confirm.", self.get_color(6))
    
            for i, name in enumerate(distros):
                y = box_y + 5 + i
                prefix = "➤ " if i == selected else "  "
                color = self.get_color(2 if i == selected else 6)
                self.safe_addstr(y, box_x + 6, f"{prefix}{name}", color)
    
            self.stdscr.refresh()
            key = self.stdscr.getch()
    
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(distros) - 1:
                selected += 1
            elif key == ord('\n'):
                self.pretty_name = self.distros[self.highlighted_distro]  # ✅ store in pretty_name
                self.current_screen = 'installing'
                self.installing = True
                self.install_thread = threading.Thread(target=self.run_installation)
                self.install_thread.start()

            elif key in (ord('q'), ord('Q')):
                return False

    def show_addons_screen(self):
        """Show addons selection screen"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Draw main box
        box_width = min(70, w - 4)
        box_height = min(18, h - 4)
        box_x = (w - box_width) // 2
        box_y = (h - box_height) // 2
        
        self.draw_box(box_y, box_x, box_height, box_width, "Installation Options")
        
        # Options
        options_y = box_y + 2
        options = [
            ("Install Player2 Application", True),
            ("Apply WebKit Patches", True),
            ("Install P2Monitor Service", False)
        ]
        
        self.safe_addstr(options_y, box_x + 2, "Select installation components:", self.get_color(2))
        self.safe_addstr(options_y + 1, box_x + 2, "(Use SPACE to toggle, ENTER to continue)", self.get_color(6))
        
        selected = 0
        option_states = [opt[1] for opt in options]
        
        while True:
            # Clear previous options
            for i in range(len(options)):
                y_pos = options_y + 3 + i * 2
                self.safe_addstr(y_pos, box_x + 4, " " * (box_width - 8))
            
            # Display options
            for i, (option, _) in enumerate(options):
                y_pos = options_y + 3 + i * 2
                checkbox = "[X]" if option_states[i] else "[ ]"
                
                if i == selected:
                    self.safe_addstr(y_pos, box_x + 4, f"> {checkbox} {option}", self.get_color(2))
                else:
                    self.safe_addstr(y_pos, box_x + 4, f"  {checkbox} {option}", self.get_color(6))
            
            # Instructions
            inst_y = options_y + 3 + len(options) * 2 + 1
            if inst_y < box_y + box_height - 4:
                self.safe_addstr(inst_y, box_x + 2, "Use UP/DOWN arrows to navigate", self.get_color(5))
                self.safe_addstr(inst_y + 1, box_x + 2, "Press SPACE to toggle, ENTER to install", self.get_color(5))
                self.safe_addstr(inst_y + 2, box_x + 2, "Press 'q' to quit", self.get_color(5))
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(options) - 1:
                selected += 1
            elif key == ord(' '):
                # Don't allow disabling Player2 application
                if selected != 0:
                    option_states[selected] = not option_states[selected]
            elif key == ord('\n') or key == ord('\r') or key == 10:
                self.install_patches = option_states[1]
                self.install_monitor = option_states[2]
                return True
            elif key == ord('q') or key == ord('Q'):
                return False
    
    def show_privacy_policy(self):
        """Show privacy policy screen"""
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Draw main box
        box_width = min(70, w - 4)
        box_height = min(20, h - 4)
        box_x = (w - box_width) // 2
        box_y = (h - box_height) // 2
        
        self.draw_box(box_y, box_x, box_height, box_width, "Privacy Policy")
        
        policy_text = [
            "Privacy Policy for P2Monitor Service",
            "Last updated: June 12, 2025",
            "",
            "1. Introduction",
            "Welcome to P2Monitor. Your privacy is important to us.",
            "",
            "2. Who We Are",
            "OptimiHost UG (haftungsbeschränkt)",
            "Operating as a service provider for Player2 modifications",
            "",
            "3. Information We Collect",
            "We collect and process the following information:",
            "- IP addresses",
            "- System information",
            "- Hardware specifications",
            "- Operating system details",
            "- Player2 usage statistics",
            "",
            "4. How We Use Your Information",
            "This information is used to:",
            "- Improve our services",
            "- Diagnose technical issues",
            "- Provide better compatibility",
            "",
            "5. Data Storage",
            "All collected data is stored securely and",
            "processed in accordance with GDPR regulations.",
            "",
            "6. Your Rights",
            "You have the right to:",
            "- Access your data",
            "- Request data deletion",
            "- Opt out of data collection",
            "",
            "7. Contact",
            "For privacy concerns, contact:",
            "privacy@optimihost.com",
            "",
            "8. Consent",
            "By installing P2Monitor, you agree to this policy.",
            "",
            "----- End of Privacy Policy -----",
            "",
            "Use UP/DOWN arrows to scroll",
            "Press SPACE when you have read the policy"
        ]
        
        current_pos = 0
        max_display_lines = box_height - 4
        read_position = len(policy_text) - max_display_lines
        has_read = False
        
        while True:
            # Display policy text
            display_y = box_y + 2
            for i in range(max_display_lines):
                line_idx = current_pos + i
                if line_idx < len(policy_text):
                    line = policy_text[line_idx]
                    # Clear line
                    self.safe_addstr(display_y + i, box_x + 2, " " * (box_width - 4))
                    # Write new line
                    self.safe_addstr(display_y + i, box_x + 2, line[:box_width-4], 
                                   self.get_color(6))
            
            # Show scroll indicator
            if current_pos > 0:
                self.safe_addstr(box_y + 1, box_x + box_width - 3, "↑", self.get_color(5))
            if current_pos + max_display_lines < len(policy_text):
                self.safe_addstr(box_y + box_height - 2, box_x + box_width - 3, "↓", 
                               self.get_color(5))
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            if key == curses.KEY_DOWN and current_pos < len(policy_text) - max_display_lines:
                current_pos += 1
                if current_pos >= read_position:
                    has_read = True
            elif key == curses.KEY_UP and current_pos > 0:
                current_pos -= 1
            elif key == ord(' ') and has_read:
                return True
            elif key == ord('q') or key == ord('Q'):
                return False
    
    def show_installation_screen(self):
        """Show installation progress screen"""
        # Add privacy policy check for P2Monitor
        if self.install_monitor:
            if not self.show_privacy_policy():
                return False
                
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        
        # Draw main box
        box_width = min(70, w - 4)
        box_height = min(20, h - 4)
        box_x = (w - box_width) // 2
        box_y = (h - box_height) // 2
        
        self.draw_box(box_y, box_x, box_height, box_width, "Installing Player2")
        
        # Progress area
        log_lines = []
        
        def add_log(message, color_pair=6):
            log_lines.append((message, color_pair))
            self.update_progress_display(box_y, box_x, box_width, box_height, log_lines)
            time.sleep(0.1)  # Small delay for visual effect
        
        # Start installation
        add_log("Starting installation...", 5)
        
        try:
            # Install system packages
            add_log("Installing system packages...", 2)
            self.install_system_packages(add_log)
            
            # Download Player2
            add_log("Downloading Player2 AppImage...", 2)
            self.install_player2(add_log)
            
            # Apply patches if selected
            if self.install_patches:
                add_log("Applying WebKit patches...", 2)
                self.apply_patches(add_log)
            
            # Setup monitor if selected
            if self.install_monitor:
                add_log("Setting up P2Monitor service...", 2)
                self.setup_monitor_service(add_log)
            
            # Create uninstaller
            add_log("Creating uninstaller...", 2)
            self.create_uninstaller(add_log)
            
            add_log("Installation completed successfully!", 3)
            add_log(f"Player2 installed to: {self.appimage_path}", 6)
            add_log("To uninstall, run: sudo p2uninstall", 5)
            add_log("Press any key to exit...", 5)
            
        except Exception as e:
            add_log(f"Installation failed: {str(e)}", 4)
            add_log("Press any key to exit...", 5)
        
        # Wait for key press
        self.stdscr.getch()
    
    def update_progress_display(self, box_y, box_x, box_width, box_height, log_lines):
        """Update the progress display"""
        # Clear content area
        for i in range(1, box_height - 1):
            if box_y + i < self.stdscr.getmaxyx()[0]:
                self.safe_addstr(box_y + i, box_x + 1, " " * (box_width - 2))
        
        # Display log lines
        display_lines = log_lines[-(box_height - 4):]  # Show lines that fit
        for i, (line, color_pair) in enumerate(display_lines):
            if i < box_height - 3:
                # Truncate line if too long
                max_line_len = box_width - 4
                if len(line) > max_line_len:
                    line = line[:max_line_len - 3] + "..."
                self.safe_addstr(box_y + 2 + i, box_x + 2, line, self.get_color(color_pair))
        
        self.stdscr.refresh()
    
    def run_command(self, cmd, log_func=None):
        """Run a command and capture real-time output"""
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        def read_output(pipe, is_error=False):
            for line in pipe:
                line = line.strip()
                if line:
                    if is_error:
                        self.logger.error(line)
                        if log_func:
                            log_func(f"ERROR: {line}", 4)
                    else:
                        self.logger.info(line)
                        if log_func:
                            log_func(line, 6)
                    
                    # Ensure screen updates
                    if log_func:
                        self.stdscr.refresh()
        
        # Create threads for reading stdout and stderr
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, True))
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Wait for completion
        process.wait()
        stdout_thread.join()
        stderr_thread.join()
        
        return process.returncode

    def install_system_packages(self, log_func):
        """Install system packages based on distribution"""
        self.logger.info(f"Installing packages for {self.pretty_name}")
        
        if "Arch" or "EndeavourOS" in self.pretty_name:
            log_func("Detected Arch Linux")
            cmd = ['pacman', '-S', '--needed', '--noconfirm',
                   'webkit2gtk-4.1', 'base-devel', 'curl', 'wget',
                   'file', 'openssl', 'appmenu-gtk-module',
                   'libappindicator-gtk3', 'librsvg']
        elif any(name in self.pretty_name for name in ["Ubuntu", "Debian", "Pop!_OS", "Linux Mint", "Kali GNU/Linux Rolling"]):
            log_func("Detected Debian-based OS")
            subprocess.run(['apt', 'update'], capture_output=True)
            cmd = ['apt', 'install', '-y',
                   'libwebkit2gtk-4.1-dev', 'build-essential', 'curl', 'wget', 'file',
                   'libxdo-dev', 'libssl-dev', 'libayatana-appindicator3-dev', 'librsvg2-dev']
        elif any(name in self.pretty_name for name in ["Fedora", "Bazzite 42 (FROM Fedora Silverblue)"]):
            log_func("Detected Fedora based OS")
            cmd = ['dnf', 'install', '-y',
                   'webkit2gtk4.1-devel', 'openssl-devel', 'curl', 'wget', 'file',
                   'libappindicator-gtk3-devel', 'librsvg2-devel']
        elif "Gentoo" in self.pretty_name:
            log_func("Detected Gentoo")
            cmd = ['emerge', '--ask=n',
                   'net-libs/webkit-gtk:4.1', 'dev-libs/libappindicator',
                   'net-misc/curl', 'net-misc/wget', 'sys-apps/file']
        elif "openSUSE" in self.pretty_name:
            log_func("Detected openSUSE")
            cmd = ['zypper', 'in', '-y',
                   'webkit2gtk3-devel', 'libopenssl-devel', 'curl', 'wget', 'file',
                   'libappindicator3-1', 'librsvg-devel']
        elif "Alpine" in self.pretty_name:
            log_func("Detected Alpine")
            cmd = ['apk', 'add',
                   'build-base', 'webkit2gtk', 'curl', 'wget', 'file',
                   'openssl', 'libayatana-appindicator-dev', 'librsvg']
        else:
            raise Exception(f"Unsupported distribution: {self.pretty_name}")
        
        log_func(f"Running: {' '.join(cmd)}")
        self.logger.info(f"Running command: {' '.join(cmd)}")
        
        returncode = self.run_command(cmd, log_func)
        if returncode != 0:
            msg = "Package installation failed"
            self.logger.error(msg)
            log_func(msg, 4)
        else:
            msg = "System packages installed successfully"
            self.logger.info(msg)
            log_func(msg, 3)

    def install_player2(self, log_func):
        """Download and install Player2 AppImage"""
        try:
            # Create directory
            player2_dir = os.path.join(self.home_dir, 'player2')
            os.makedirs(player2_dir, exist_ok=True)
            self.logger.info("Created player2 directory")
            log_func("Created player2 directory")

            # Download with curl instead of wget for better error handling
            download_cmd = [
                'curl', '-L', '-o', self.appimage_path,
                '--retry', '3',  # Retry up to 3 times
                '--retry-delay', '2',  # Wait 2 seconds between retries
                '--connect-timeout', '10',  # Connection timeout
                '--progress-bar',  # Show progress
                self.latest_ver_p2
            ]

            log_func(f"Downloading Player2...")
            self.logger.info(f"Running download command: {' '.join(download_cmd)}")
            
            # Run download command
            result = subprocess.run(download_cmd, capture_output=True, text=True)
            
            # Check if file exists and has content
            if not os.path.exists(self.appimage_path) or os.path.getsize(self.appimage_path) == 0:
                raise Exception("Download failed - file is empty or missing")
                
            # Make executable
            os.chmod(self.appimage_path, 0o755)
            
            # Verify file is executable
            if not os.access(self.appimage_path, os.X_OK):
                raise Exception("Failed to set executable permissions")

            msg = "Player2 AppImage downloaded and installed successfully"
            self.logger.info(msg)
            log_func(msg, 3)
            
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}")
            if os.path.exists(self.appimage_path):
                os.remove(self.appimage_path)
            raise Exception(f"Failed to install Player2: {str(e)}")
    
    def apply_patches(self, log_func):
        """Apply WebKit patches"""
        try:
            home = self.home_dir
            env_line = "export WEBKIT_DISABLE_DMABUF_RENDERER=1"
            
            shells = {
                "bash": os.path.join(home, ".bashrc"),
                "zsh": os.path.join(home, ".zshrc"),
            }
            
            installed_shells = []
            for shell_name, shell_path in shells.items():
                if shutil.which(shell_name) or os.path.exists(shell_path):
                    installed_shells.append(shell_name)
            
            if not installed_shells:
                log_func("No shell config files found, creating .bashrc", 2)
                installed_shells = ["bash"]
            
            for shell in installed_shells:
                rc_path = shells[shell]
                
                # Create file if it doesn't exist
                if not os.path.exists(rc_path):
                    open(rc_path, "w").close()
                
                # Read existing content
                with open(rc_path, "r") as f:
                    content = f.read()
                
                # Check if patch already exists
                if env_line not in content:
                    with open(rc_path, "a") as f:
                        f.write(f"\n# Added by Player2 installer\n{env_line}\n")
                    log_func(f"Patch applied to {shell}", 3)
                else:
                    log_func(f"Patch already exists in {shell}", 2)
            
            log_func("WebKit patches applied successfully", 3)
        except Exception as e:
            raise Exception(f"Failed to apply patches: {str(e)}")
    
    def setup_monitor_service(self, log_func):
        """Setup P2Monitor service"""
        try:
            # Create monitor directory
            os.makedirs('/etc/p2monitor', exist_ok=True)
            log_func("Created monitor directory")
            
            # Create monitor script
            monitor_script = '''#!/usr/bin/env python3
import os
import time
from pathlib import Path

WARNING_TEXT = """--- Player2 Log --
This is ok. -- OptimiDev

!!! WARNING !!!
PLEASE MAKE SURE THAT THIS IS NOT CAUSED BY P2Installer Patches
DO NOT REPORT THIS TO PLAYER2, REPORT THIS TO https://github.com/OptimiDEV/P2Installer/issues
"""

def monitor_logs():
    log_dir = Path(os.path.expanduser("~/.config/game.player2.client.playground/logs"))
    while True:
        try:
            if log_dir.exists():
                for log_file in log_dir.glob("*"):
                    if log_file.is_file():
                        try:
                            with open(log_file, "r+") as f:
                                content = f.read()
                                if WARNING_TEXT not in content:
                                    f.seek(0, 0)
                                    f.write(WARNING_TEXT + "\\n" + content)
                        except Exception:
                            pass
        except Exception:
            pass
        time.sleep(5)

if __name__ == "__main__":
    monitor_logs()
'''
            
            with open('/etc/p2monitor/monitor.py', 'w') as f:
                f.write(monitor_script)
            log_func("Created monitor script")
            
            # Create service file
            service_content = '''[Unit]
Description=Player2 Log Monitor
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /etc/p2monitor/monitor.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
'''
            
            with open('/etc/systemd/system/p2monitor.service', 'w') as f:
                f.write(service_content)
            log_func("Created systemd service")
            
            # Set permissions and enable service
            subprocess.run(['chmod', '+x', '/etc/p2monitor/monitor.py'])
            subprocess.run(['systemctl', 'daemon-reload'], capture_output=True)
            result = subprocess.run(['systemctl', 'enable', 'p2monitor'], capture_output=True)
            if result.returncode == 0:
                subprocess.run(['systemctl', 'start', 'p2monitor'], capture_output=True)
                log_func("P2Monitor service installed and started", 3)
            else:
                log_func("P2Monitor service created (manual start required)", 2)
                
        except Exception as e:
            raise Exception(f"Failed to setup monitor service: {str(e)}")
    
    def create_uninstaller(self, log_func):
        """Create and set up the uninstaller script"""
        try:
            # Create uninstaller script content
            uninstaller = '''#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import pwd

def remove_player2():
    """Remove Player2 application"""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        home_dir = pwd.getpwnam(sudo_user).pw_dir
        player2_dir = os.path.join(home_dir, "player2")
        if os.path.exists(player2_dir):
            shutil.rmtree(player2_dir)
            print("✓ Removed Player2 application")
        else:
            print("Player2 directory not found")

def remove_webkit_patches():
    """Remove WebKit patches from shell config files"""
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        home_dir = pwd.getpwnam(sudo_user).pw_dir
        shell_files = [
            os.path.join(home_dir, ".bashrc"),
            os.path.join(home_dir, ".zshrc")
        ]
        
        for rc_file in shell_files:
            if os.path.exists(rc_file):
                with open(rc_file, "r") as f:
                    lines = f.readlines()
                
                with open(rc_file, "w") as f:
                    for line in lines:
                        if "WEBKIT_DISABLE_DMABUF_RENDERER" not in line:
                            f.write(line)
        print("✓ Removed WebKit patches")

def remove_p2monitor():
    """Remove P2Monitor service"""
    try:
        subprocess.run(["systemctl", "stop", "p2monitor"], capture_output=True)
        subprocess.run(["systemctl", "disable", "p2monitor"], capture_output=True)
        
        if os.path.exists("/etc/systemd/system/p2monitor.service"):
            os.remove("/etc/systemd/system/p2monitor.service")
        
        if os.path.exists("/etc/p2monitor"):
            shutil.rmtree("/etc/p2monitor")
            
        subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
        print("✓ Removed P2Monitor service")
    except Exception as e:
        print(f"Error removing P2Monitor: {e}")

def main():
    if os.geteuid() != 0:
        print("This script must be run with sudo privileges.")
        print("Please run: sudo p2uninstall")
        sys.exit(1)

    print("P2Installer Uninstaller")
    print("----------------------")
    print("Select components to remove:")
    print("1. Player2 Application")
    print("2. WebKit Patches")
    print("3. P2Monitor Service")
    print("4. All Components")
    print("5. Cancel")
    
    choice = input("Enter your choice (1-5): ")
    
    if choice == "1":
        remove_player2()
    elif choice == "2":
        remove_webkit_patches()
    elif choice == "3":
        remove_p2monitor()
    elif choice == "4":
        remove_player2()
        remove_webkit_patches()
        remove_p2monitor()
    elif choice == "5":
        print("Uninstallation cancelled.")
        sys.exit(0)
    else:
        print("Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

            # Create uninstaller script
            script_path = "/usr/local/bin/p2uninstall"
            with open(script_path, "w") as f:
                f.write(uninstaller)
            
            # Make executable
            os.chmod(script_path, 0o755)
            log_func("Created uninstaller script: p2uninstall", 3)

        except Exception as e:
            raise Exception(f"Failed to create uninstaller: {str(e)}")

def main():
    try:
        installer = Player2ConsoleInstaller()
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
