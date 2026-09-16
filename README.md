# Port - Advance Internet Port Tool

[![Kali Linux Supported](https://img.shields.io/badge/Kali_Linux-Supported-blue?logo=kalilinux&logoColor=white)](https://www.kali.org)
[![Termux Supported](https://img.shields.io/badge/Termux-Supported-green?logo=android&logoColor=white)](https://termux.dev)
[![Bash Shell](https://img.shields.io/badge/Language-Bash_%26_Python3-orange?logo=gnubash&logoColor=white)](https://www.gnu.org/software/bash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Advanced, High-Performance Internet Port Audit & Networking Suite** specifically engineered for **Kali Linux** and **Termux (Android)** environments.

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

---

## 🌟 Key Highlights

- **Dual-Platform Native Design**: Runs natively on both **Kali Linux** (desktop / penetration testing distribution) and **Termux** (Android mobile terminal).
- **Zero-Dependency Resilience**: Powered by an embedded high-speed multi-threaded networking engine with pure Bash `/dev/tcp` fallback. Works out-of-the-box even without third-party packages installed.
- **Ultra-Fast Multi-threaded Scanner**: Scans up to 1,000 ports in fractions of a second with configurable concurrency (1-500 threads) and timeouts.
- **Deep Service & Banner Fingerprinting**: Handshakes with target services to extract exact version strings, HTTP server headers, HTML page titles, SSL/TLS certificates (Common Name, Issuer, Expiry), SSH versions, and database signatures (MySQL, Redis, etc.).
- **Local Port Inspector & Killer**: Lists all active listening TCP/UDP sockets with Process IDs (PIDs) and process names; includes a one-click/CLI process termination tool (`port -k <port>`) to free up occupied ports.
- **Port Listener & Reverse Shell Catcher**: Emulates Netcat (`nc -lvnp`) for catching reverse shells, receiving exfiltrated files, or testing raw TCP/UDP streams.
- **Intrusion Honeypot & Payload Logger**: Simulates vulnerable services (SSH, FTP, HTTP, SMTP, Telnet) and logs all inbound probe attempts, client IPs, timestamps, and hex/ASCII payloads to `logs/`.
- **TCP Port Forwarder & Proxy Relay**: Bidirectional stream redirection from a local port to a remote destination with real-time transfer counters and bandwidth stats.
- **Outbound Firewall Egress Tester**: Probes 26 critical ports to discover which outbound connections your ISP, carrier, or corporate firewall is filtering.
- **Curated Port & CVE Knowledge Base**: Searchable offline database of 200+ ports with service classifications, security risk ratings (Low to Critical), and known exploit vectors (MS17-010 EternalBlue, Log4j, Spring4Shell, unauthenticated Redis/Docker/Kubernetes).
- **Modern Responsive HTML Reports**: Produces a Cyberpunk/SOC-themed dark mode dashboard report with statistics cards, risk badges, and interactive JavaScript search filtering.

---

## 📋 Features Matrix

| Feature | Description | Kali Linux | Termux (Android) |
| :--- | :--- | :---: | :---: |
| **Fast TCP Connect Scan** | Concurrent multi-threaded port scanner | ✅ Full | ✅ Full |
| **Deep Banner Grabbing** | HTTP headers, TLS certs, SSH/FTP/DB banners | ✅ Full | ✅ Full |
| **UDP Port Scanner** | DNS, NTP, SNMP, DHCP, TFTP, Syslog probes | ✅ Full | ✅ Full |
| **SYN Stealth Scan** | Raw packet SYN scanning (via Nmap) | ✅ Root/Sudo | ⚠️ Requires Root (tsu) |
| **Local Port Inspector** | List listening sockets, PIDs, processes | ✅ Full | ✅ User Sockets |
| **Port Killer** | Force terminate process holding port | ✅ Full | ✅ User Processes |
| **Port Listener** | Interactive two-way TCP/UDP listener | ✅ Full | ✅ Ports ≥ 1024 (or root) |
| **Honeypot Logger** | Fake banner simulation & payload dumping | ✅ Full | ✅ Ports ≥ 1024 (or root) |
| **Port Forwarder** | Local-to-remote TCP streaming relay | ✅ Full | ✅ Full |
| **Egress Firewall Test** | Outbound port filtering discovery | ✅ Full | ✅ Full |
| **Port Knowledgebase** | 200+ ports with security risk & CVE notes | ✅ Full | ✅ Full |
| **Multi-format Export** | HTML Dashboard, JSON, CSV, TXT | ✅ Full | ✅ Full |

---

## 🚀 Installation

### Option 1: Quick Install (Kali Linux & Debian / Ubuntu)

```bash
# Clone the repository
git clone https://github.com/lifeemotorola/Port.git
cd Port

# Make scripts executable
chmod +x port.sh install.sh

# Run automated installer (creates global 'port' command)
./install.sh
```

### Option 2: Termux (Android) Installation

Open Termux on Android and run:

```bash
# Update Termux packages
pkg update -y && pkg install -y git python curl

# Clone the repository
git clone https://github.com/lifeemotorola/Port.git
cd Port

# Set executable permission
chmod +x port.sh install.sh

# Run installer (installs into $PREFIX/bin/port)
./install.sh
```

> **Note for Termux users**: Binding to ports below `1024` (such as port 80 or 443) requires Android root access (`tsu`). You can run listeners, honeypots, and forwarders on ports `1024-65535` without root!

---

## 🖥️ Usage & Command Reference

You can run `port` either in **Interactive Menu Mode** or via **CLI Flags**.

### 1. Interactive Menu Mode

Simply run the script with no arguments:

```bash
port
# or
./port.sh
```

This launches the interactive terminal menu:

```
  ██████╗  ██████╗ ██████╗ ████████╗
  ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
  ██████╔╝██║   ██║██████╔╝   ██║   
  ██╔═══╝ ██║   ██║██╔══██╗   ██║   
  ██║     ╚██████╔╝██║  ██║   ██║   
  ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
       Advance Internet Port Tool v2.1.0
    [ Kali Linux & Termux Edition ]

MAIN MENU:

  [1]  Fast TCP Port Scanner (Top Ports / Range / Full)
  [2]  Deep Service & Banner Detector (Fingerprint / HTTP / SSL)
  [3]  UDP Port Scanner (DNS, NTP, SNMP, DHCP, etc.)
  [4]  Local Port Inspector (View Active Listening Sockets & PIDs)
  [5]  Kill Process on Port (Free up occupied port)
  [6]  Port Listener / Reverse Shell Catcher (Netcat Mode)
  [7]  Port Honeypot & Intrusion Monitor (Detect & Log Attacks)
  [8]  TCP Port Forwarder / Relay Proxy (Local -> Remote)
  [9]  Firewall Outbound Egress Checker (Find Blocked Ports)
  [10] Network Interfaces & Public IP Lookup
  [11] Port Knowledgebase & Vulnerability Directory (Search 200+ Ports)
  [12] Nmap Advanced Scan Integration
  [13] Install / Update Dependencies (Kali & Termux)
  [0]  Exit
```

---

### 2. Non-Interactive CLI Mode (Scripting & Automation)

```bash
./port.sh -t <target> [options]
```

#### CLI Flags:

| Flag | Parameter | Description |
| :--- | :--- | :--- |
| `-t, --target` | `<host>` | Target IP or hostname (e.g. `192.168.1.1` or `scanme.nmap.org`) |
| `-p, --ports` | `<ports>` | Ports: `top20`, `top100`, `top1000`, `all`, `wellknown`, or ranges `80,443,8000-8080` (Default: `top100`) |
| `-m, --mode` | `<mode>` | Scan mode: `fast` (default), `deep` (banner + TLS cert), `udp`, `syn`, `nmap` |
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

### 1. Rapid Network Reconnaissance

```bash
# Scan Top 20 most critical ports on a router/target
port -t 192.168.1.1 -p top20

# Scan Top 1000 standard ports with 200 concurrent threads
port -t scanme.nmap.org -p top1000 -T 200
```

### 2. Deep Banner Grabbing & HTML Vulnerability Report

```bash
# Probe services, extract HTTP server headers, TLS certificates, and save to HTML
port -t example.com -p 21,22,80,443,3306,8080 -m deep -o reports/audit.html
```

### 3. UDP Port Scanning

```bash
# Probe UDP ports for DNS, NTP, SNMP, DHCP, and TFTP
port -t 192.168.1.1 -p 53,67,69,123,161 -m udp
```

### 4. Local Port Management (Find & Kill Occupied Ports)

```bash
# View what processes are listening locally
port -i

# Kill the process occupying port 8080
port -k 8080 --force
```

### 5. Catch a Reverse Shell / TCP Listener

```bash
# Listen on port 4444 (Netcat replacement)
port -l 4444

# Save exfiltrated session stream to disk
port -l 4444 -o logs/session.txt
```

### 6. Honeypot Intrusion Logging

```bash
# Deploy an SSH honeypot on port 2222 that logs attacker payloads and passwords
port --honeypot 2222 --service ssh
```

### 7. TCP Port Forwarding / Proxying

```bash
# Expose remote web server (192.168.1.100:80) locally on 127.0.0.1:8080
port -f 8080:192.168.1.100:80
```

### 8. Firewall Egress Testing

```bash
# Discover which outbound ports are restricted by your ISP or Wi-Fi hotspot
port -e
```

### 9. Port Security Knowledge Base Lookup

```bash
# Find security vulnerabilities and attack vectors for SMB (port 445)
port -q 445

# Search for all database-related ports and CVE exploit notes
port -q database
```

---

## 📊 Sample HTML Report Output

When exporting to `.html` (`-o reports/scan.html`), Port generates a self-contained, responsive dark dashboard:

- **Metric Cards**: Total Scanned, Open Ports Found, Elapsed Time, Critical/High Risk Count.
- **Interactive Search Filter**: Type in the search box to filter results instantaneously in real time.
- **Service & Risk Badges**: Color-coded risk indicators (`Critical`, `High`, `Medium`, `Low`, `Informational`).
- **TLS Details**: Subject, Issuer, and Expiration parsed from peer SSL certificates.

---

## 📁 Repository Structure

```
Port/
├── port.sh               # Master executable CLI & Interactive Menu script (.sh)
├── install.sh            # Global installer for Kali Linux & Termux
├── core/
│   ├── engine.py         # Multi-threaded networking & socket engine
│   ├── ports_db.json     # Knowledge base of 200+ ports with CVE & risk notes
│   └── build_db.py       # Knowledge base generator & maintenance script
├── tests/
│   └── test_port.sh      # Automated integration test suite (14 test cases)
├── reports/              # Default destination for generated audit reports
├── logs/                 # Default destination for honeypot & listener logs
└── README.md             # Complete documentation
```

---

## 🧪 Testing

The repository includes an automated integration test suite:

```bash
./tests/test_port.sh
```

All 14 integration test cases verify:
- CLI argument handling and version strings
- Socket scanner engines and banner grabbing
- HTML, JSON, and CSV report exports
- Process termination on occupied ports
- TCP forwarder streaming
- Honeypot intrusion logging and payload capture

---

## ⚖️ Legal Disclaimer

This tool is designed for educational purposes, legitimate system administration, and authorized security assessments only. Do not scan or probe targets without explicit authorization from the system owner. The authors assume no liability for misuse or damage caused by this software.
