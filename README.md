<h1>🎮 Optimi's P2Installer</h1>
[![StandWithUkraine](https://github.com/user-attachments/assets/e8bbe60a-a9bb-4336-866e-4023903a7e0a)](https://stand-with-ukraine.pp.ua/)


<p><strong>Run Player2 (from <a href="https://player2.game">player2.game</a>) on Linux with ease.</strong><br>
<em>This is a 3rd party installer app, not an official Player2 product.</em></p>

<p>Optimi's P2Installer is a cross-distro Python installer that automates the setup of dependencies, environment variables, and the latest Player2.AppImage.</p>

<hr>

<h2>🤖 What is Player2?</h2>

<p><strong>Player2</strong> (available at <a href="https://player2.game">player2.game</a>) is an AI-powered platform designed to enhance gaming experiences by providing intelligent in-game assistance. It enables gamers to:</p>

<ul>
  <li><strong>Integrate AI companions</strong> into games like Minecraft, offering dynamic interactions and support.</li>
  <li><strong>Access AI APIs</strong> for indie game developers to create custom AI-driven content.</li>
  <li><strong>Explore and share AI mods and games</strong>, fostering a community of creators and players.</li>
</ul>

<hr>

<h2>✅ P2Installer Features</h2>

<ul>
  <li><strong>Cross-distro support</strong>: Works on Arch Linux, Ubuntu/Debian, Fedora, Gentoo, openSUSE, and Alpine Linux.</li>
  <li><strong>Automated setup</strong>: Installs necessary dependencies, patches environment variables, and downloads the latest Player2.AppImage.</li>
</ul>

<hr>

<h2>⚙️ Requirements</h2>

<ul>
  <li>Linux (any major distro)</li>
  <li><code>sudo</code> privileges</li>
  <li><code>Python 3.6</code> or later</li>
</ul>

<hr>

<h2>🚀 Installation</h2>

<p>Run the following command to install Player2:</p>

<pre><code>bash -c 'curl -fsSL https://raw.githubusercontent.com/OptimiDEV/P2Installer/main/main.py -o /tmp/p2installer.py &amp;&amp; sudo python3 /tmp/p2installer.py'
</code></pre>

<p>This script will:</p>

<ol>
  <li>Detect your Linux distribution.</li>
  <li>Install required dependencies.</li>
  <li>Download the latest Player2.AppImage.</li>
  <li>Make the AppImage executable.</li>
  <li>Patch your shell environment variables.</li>
</ol>

<hr>

<h2>🛠 Behind the Scenes</h2>

<p>The installer script performs the following steps:</p>

<ol>
  <li><strong>Check for sudo privileges</strong>: Ensures the script is run with appropriate permissions.</li>
  <li><strong>Display ASCII banner</strong>: Shows a welcome message with the Optimi logo.</li>
  <li><strong>Detect operating system</strong>: Identifies the Linux distribution using <code>platform.freedesktop_os_release()</code>.</li>
  <li><strong>Install dependencies</strong>: Based on the detected OS, installs necessary packages using the appropriate package manager.</li>
  <li><strong>Download Player2.AppImage</strong>: Fetches the latest version of the Player2 AppImage from the official source.</li>
  <li><strong>Set executable permissions</strong>: Makes the downloaded AppImage executable.</li>
</ol>

<hr>

<h2>🛡️ Notes &amp; Cleanup</h2>

<ul>
  <li><strong>Uninstallation</strong>: To remove Player2, use <code>sudo p2uninstall</code>
</ul>

<hr>

<p><em>That's all.</em></p>
