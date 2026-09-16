#!/usr/bin/env bash
# ==============================================================================
# Port - Advance Internet Port Tool
# Specialized for Kali Linux & Termux (Android)
# Author: lifeemotorola
# Repository: https://github.com/lifeemotorola/Port
# Version: 2.1.0
# ==============================================================================

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_VERSION="2.1.0"

# Directories
CORE_DIR="$SCRIPT_DIR/core"
LOGS_DIR="$SCRIPT_DIR/logs"
REPORTS_DIR="$SCRIPT_DIR/reports"
mkdir -p "$LOGS_DIR" "$REPORTS_DIR"

# ANSI Colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_RED="\033[0;31m"
C_GREEN="\033[0;32m"
C_YELLOW="\033[1;33m"
C_BLUE="\033[0;34m"
C_PURPLE="\033[0;35m"
C_CYAN="\033[0;36m"
C_WHITE="\033[1;37m"
C_GRAY="\033[0;90m"

# Handle NO_COLOR environment or flag
if [ -n "$NO_COLOR" ] || [ "$1" = "--no-color" ]; then
    C_RESET=""
    C_BOLD=""
    C_RED=""
    C_GREEN=""
    C_YELLOW=""
    C_BLUE=""
    C_PURPLE=""
    C_CYAN=""
    C_WHITE=""
    C_GRAY=""
fi

# Detect Environment (Kali Linux vs Termux vs Generic Linux)
detect_environment() {
    IS_TERMUX=false
    IS_KALI=false
    IS_ROOT=false
    OS_NAME="Linux"
    PKG_MGR="apt"
    INSTALL_CMD="sudo apt-get install -y"

    [ "$(id -u)" -eq 0 ] && IS_ROOT=true

    if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ] || [[ "$PREFIX" == *"com.termux"* ]]; then
        IS_TERMUX=true
        OS_NAME="Termux (Android)"
        PKG_MGR="pkg"
        INSTALL_CMD="pkg install -y"
        BIN_INSTALL_DIR="${PREFIX:-/data/data/com.termux/files/usr}/bin"
    elif [ -f "/etc/os-release" ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        if [[ "$ID" == "kali" ]] || [[ "$ID_LIKE" == *"kali"* ]]; then
            IS_KALI=true
            OS_NAME="Kali Linux"
            PKG_MGR="apt"
            INSTALL_CMD="sudo apt-get update && sudo apt-get install -y"
            BIN_INSTALL_DIR="/usr/local/bin"
        elif [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]] || [[ "$ID_LIKE" == *"debian"* ]]; then
            OS_NAME="Debian/Ubuntu (${ID})"
            PKG_MGR="apt"
            INSTALL_CMD="sudo apt-get update && sudo apt-get install -y"
            BIN_INSTALL_DIR="/usr/local/bin"
        elif [[ "$ID" == "arch" ]] || [[ "$ID_LIKE" == *"arch"* ]]; then
            OS_NAME="Arch Linux"
            PKG_MGR="pacman"
            INSTALL_CMD="sudo pacman -Sy --noconfirm"
            BIN_INSTALL_DIR="/usr/local/bin"
        else
            OS_NAME="${PRETTY_NAME:-Linux}"
            BIN_INSTALL_DIR="/usr/local/bin"
        fi
    else
        BIN_INSTALL_DIR="/usr/local/bin"
    fi
}

detect_environment

# Python check and Engine locator
find_engine() {
    if [ -f "$CORE_DIR/engine.py" ]; then
        ENGINE_PATH="$CORE_DIR/engine.py"
    elif [ -f "/opt/port/core/engine.py" ]; then
        ENGINE_PATH="/opt/port/core/engine.py"
    elif [ -n "$PREFIX" ] && [ -f "$PREFIX/opt/port/core/engine.py" ]; then
        ENGINE_PATH="$PREFIX/opt/port/core/engine.py"
    else
        ENGINE_PATH=""
    fi

    # Check python3
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
    else
        PYTHON_CMD=""
    fi
}

find_engine

# ASCII Art Banner
print_banner() {
    echo -e "${C_CYAN}${C_BOLD}"
    cat << "EOF"
  ██████╗  ██████╗ ██████╗ ████████╗
  ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
  ██████╔╝██║   ██║██████╔╝   ██║   
  ██╔═══╝ ██║   ██║██╔══██╗   ██║   
  ██║     ╚██████╔╝██║  ██║   ██║   
  ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
EOF
    echo -e "${C_RESET}"
    echo -e "   ${C_WHITE}${C_BOLD}Advance Internet Port Tool${C_RESET} ${C_GRAY}v${APP_VERSION}${C_RESET}"
    echo -e "   ${C_PURPLE}[ Kali Linux & Termux Edition ]${C_RESET}"
    echo -e "   ${C_CYAN}OS:${C_RESET} ${OS_NAME} ${C_GRAY}|${C_RESET} ${C_CYAN}User:${C_RESET} $(whoami) $([ "$IS_ROOT" = true ] && echo -e "${C_GREEN}[ROOT]${C_RESET}" || echo -e "${C_YELLOW}[USER]${C_RESET}")"
    echo -e "${C_GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${C_RESET}\n"
}

# Help Manual
show_help() {
    print_banner
    echo -e "${C_BOLD}USAGE:${C_RESET}"
    echo -e "  ./port.sh                        Launch interactive menu UI"
    echo -e "  ./port.sh -t <target> [options]  Non-interactive CLI mode\n"

    echo -e "${C_BOLD}SCANNING OPTIONS:${C_RESET}"
    echo -e "  ${C_CYAN}-t, --target <host>${C_RESET}        Target IP or domain (e.g. 192.168.1.1, scanme.org)"
    echo -e "  ${C_CYAN}-p, --ports <ports>${C_RESET}        Ports: ${C_YELLOW}top20${C_RESET}, ${C_YELLOW}top100${C_RESET}, ${C_YELLOW}top1000${C_RESET}, ${C_YELLOW}all${C_RESET}, ${C_YELLOW}wellknown${C_RESET}"
    echo -e "                             Or ranges/lists: ${C_YELLOW}80,443,8000-8080${C_RESET} (Default: top100)"
    echo -e "  ${C_CYAN}-m, --mode <mode>${C_RESET}          Scan mode: ${C_YELLOW}fast${C_RESET} (default), ${C_YELLOW}deep${C_RESET} (banner+SSL), ${C_YELLOW}udp${C_RESET}, ${C_YELLOW}nmap${C_RESET}"
    echo -e "  ${C_CYAN}-T, --threads <num>${C_RESET}        Concurrency threads (Default: 100, range: 1-500)"
    echo -e "  ${C_CYAN}-W, --timeout <sec>${C_RESET}        Socket timeout in seconds (Default: 1.5)"
    echo -e "  ${C_CYAN}-o, --output <file>${C_RESET}        Export report: .txt, .json, .csv, or .html\n"

    echo -e "${C_BOLD}TOOLS & UTILITIES:${C_RESET}"
    echo -e "  ${C_CYAN}-i, --inspect${C_RESET}              Inspect local active listening ports and processes"
    echo -e "  ${C_CYAN}-k, --kill <port>${C_RESET}          Kill the process occupying the specified port"
    echo -e "  ${C_CYAN}-l, --listen <port>${C_RESET}         Start TCP/UDP socket listener (Reverse Shell Catcher)"
    echo -e "  ${C_CYAN}-u, --udp${C_RESET}                  Use UDP protocol (for scan or listener)"
    echo -e "  ${C_CYAN}--honeypot <port>${C_RESET}          Start intrusion honeypot & payload logger on <port>"
    echo -e "  ${C_CYAN}--service <name>${C_RESET}           Honeypot service emulation: ssh, ftp, http, smtp, telnet"
    echo -e "  ${C_CYAN}-f, --forward <lport:rhost:rport>${C_RESET}"
    echo -e "                             Forward local port to remote destination (TCP proxy)"
    echo -e "  ${C_CYAN}-e, --egress${C_RESET}               Test outbound firewall egress connectivity (26 ports)"
    echo -e "  ${C_CYAN}-q, --lookup <query>${C_RESET}        Search knowledgebase by port number or service keyword"
    echo -e "  ${C_CYAN}--ip${C_RESET}                       Display local network interfaces and WAN public IP"
    echo -e "  ${C_CYAN}--install${C_RESET}                  Auto-install recommended packages on Kali or Termux"
    echo -e "  ${C_CYAN}--no-color${C_RESET}                 Disable ANSI colored text"
    echo -e "  ${C_CYAN}-h, --help${C_RESET}                 Show this help screen"
    echo -e "  ${C_CYAN}-v, --version${C_RESET}              Show tool version\n"

    echo -e "${C_BOLD}PRACTICAL EXAMPLES:${C_RESET}"
    echo -e "  ${C_GRAY}# Interactive Menu UI${C_RESET}"
    echo -e "  ./port.sh\n"
    echo -e "  ${C_GRAY}# Fast scan Top 100 ports on remote target${C_RESET}"
    echo -e "  ./port.sh -t 192.168.1.1 -p top100\n"
    echo -e "  ${C_GRAY}# Deep scan with banner grabbing & HTML report${C_RESET}"
    echo -e "  ./port.sh -t example.com -p 22,80,443,8080 -m deep -o reports/example.html\n"
    echo -e "  ${C_GRAY}# Inspect what's listening locally and free port 8080${C_RESET}"
    echo -e "  ./port.sh -i"
    echo -e "  ./port.sh -k 8080\n"
    echo -e "  ${C_GRAY}# Start SSH honeypot logging intrusions${C_RESET}"
    echo -e "  ./port.sh --honeypot 2222 --service ssh\n"
    echo -e "  ${C_GRAY}# Forward local port 8080 to remote server${C_RESET}"
    echo -e "  ./port.sh -f 8080:192.168.1.50:80\n"
    echo -e "  ${C_GRAY}# Search port vulnerability database${C_RESET}"
    echo -e "  ./port.sh -q 445"
    echo -e "  ./port.sh -q redis\n"
}

# Auto Dependency Installer
install_dependencies() {
    print_banner
    echo -e "${C_CYAN}[*] Installing dependencies for ${OS_NAME}...${C_RESET}\n"

    if [ "$IS_TERMUX" = true ]; then
        echo -e "${C_YELLOW}[+] Running Termux package manager (pkg)...${C_RESET}"
        pkg update -y || apt update -y
        pkg install -y python curl netcat-openbsd socat dnsutils jq nmap iproute2 || true
    elif [ "$IS_KALI" = true ] || [ "$PKG_MGR" = "apt" ]; then
        echo -e "${C_YELLOW}[+] Running APT package manager...${C_RESET}"
        if [ "$IS_ROOT" = true ]; then
            apt-get update && apt-get install -y python3 curl netcat-traditional socat dnsutils jq nmap iproute2 || true
        else
            sudo apt-get update && sudo apt-get install -y python3 curl netcat-traditional socat dnsutils jq nmap iproute2 || true
        fi
    elif [ "$PKG_MGR" = "pacman" ]; then
        sudo pacman -Sy --noconfirm python curl openbsd-netcat socat bind-tools jq nmap iproute2 || true
    else
        echo -e "${C_YELLOW}[!] Generic system detected. Please ensure python3, curl, and nmap are installed.${C_RESET}"
    fi

    # Install global command link
    echo -e "\n${C_CYAN}[*] Setting up global 'port' command in PATH...${C_RESET}"
    chmod +x "$SCRIPT_DIR/port.sh" "$CORE_DIR/engine.py" 2>/dev/null || true

    if [ -d "$BIN_INSTALL_DIR" ] && [ -w "$BIN_INSTALL_DIR" ]; then
        ln -sf "$SCRIPT_DIR/port.sh" "$BIN_INSTALL_DIR/port" 2>/dev/null && \
        echo -e "${C_GREEN}[+] Global shortcut created: You can now run 'port' from anywhere!${C_RESET}"
    elif [ "$IS_ROOT" = true ]; then
        ln -sf "$SCRIPT_DIR/port.sh" "/usr/local/bin/port" 2>/dev/null && \
        echo -e "${C_GREEN}[+] Global shortcut created: You can now run 'port' from anywhere!${C_RESET}"
    else
        echo -e "${C_YELLOW}[*] To install system-wide, run: sudo ln -sf $(pwd)/port.sh /usr/local/bin/port${C_RESET}"
    fi

    echo -e "\n${C_GREEN}${C_BOLD}[✓] Dependency setup completed!${C_RESET}\n"
}

# Display IP and Interface Info
show_ip_info() {
    print_banner
    echo -e "${C_BOLD}LOCAL NETWORK INTERFACES:${C_RESET}"
    echo -e "${C_GRAY}------------------------------------------------------------${C_RESET}"

    if command -v ip >/dev/null 2>&1; then
        ip -o -4 addr show | while read -r line; do
            iface=$(echo "$line" | awk '{print $2}')
            ip_addr=$(echo "$line" | awk '{print $4}')
            printf "  ${C_CYAN}%-12s${C_RESET} : ${C_GREEN}%s${C_RESET}\n" "$iface" "$ip_addr"
        done
    elif command -v ifconfig >/dev/null 2>&1; then
        ifconfig | grep -E "inet |flags" | awk '{print $1, $2}'
    fi
    echo -e "${C_GRAY}------------------------------------------------------------${C_RESET}\n"

    echo -e "${C_BOLD}PUBLIC WAN IP & GEO-INFORMATION:${C_RESET}"
    echo -e "${C_GRAY}------------------------------------------------------------${C_RESET}"
    
    # Try fetching public IP with timeout
    PUB_IP=""
    for url in "https://api.ipify.org" "https://ifconfig.me/ip" "https://icanhazip.com"; do
        PUB_IP=$(curl -s --connect-timeout 2 "$url" 2>/dev/null | tr -d '[:space:]')
        [ -n "$PUB_IP" ] && break
    done

    if [ -n "$PUB_IP" ]; then
        echo -e "  ${C_CYAN}Public IP   ${C_RESET} : ${C_GREEN}${C_BOLD}${PUB_IP}${C_RESET}"
        # Try fetching IP details
        DETAILS=$(curl -s --connect-timeout 2 "https://ipinfo.io/${PUB_IP}/json" 2>/dev/null)
        if [ -n "$DETAILS" ] && command -v jq >/dev/null 2>&1; then
            ORG=$(echo "$DETAILS" | jq -r '.org // empty')
            CITY=$(echo "$DETAILS" | jq -r '.city // empty')
            COUNTRY=$(echo "$DETAILS" | jq -r '.country // empty')
            [ -n "$ORG" ] && echo -e "  ${C_CYAN}ISP / ASN   ${C_RESET} : ${ORG}"
            [ -n "$CITY" ] && echo -e "  ${C_CYAN}Location    ${C_RESET} : ${CITY}, ${COUNTRY}"
        fi
    else
        echo -e "  ${C_YELLOW}[!] Public WAN IP query timed out (Offline or Restricted Network).${C_RESET}"
    fi
    echo -e "${C_GRAY}------------------------------------------------------------${C_RESET}\n"
}

# Run Bash Fallback Scan if Python is missing
run_bash_port_scan() {
    local target="$1"
    local ports_raw="$2"
    echo -e "${C_YELLOW}[*] Python not detected. Running built-in Native Bash Socket Scanner...${C_RESET}"

    # Parse ports
    local port_list=()
    if [ "$ports_raw" = "top20" ]; then
        port_list=(21 22 23 25 53 80 110 111 135 139 143 443 445 993 995 1723 3306 3389 5900 8080)
    elif [ "$ports_raw" = "top100" ] || [ -z "$ports_raw" ]; then
        port_list=(21 22 23 25 53 80 110 111 135 139 143 443 445 993 995 1433 1521 2049 3306 3389 5432 5900 6379 8080 8443 27017)
    else
        IFS=',' read -ra ADDR <<< "$ports_raw"
        for i in "${ADDR[@]}"; do
            port_list+=("$i")
        done
    fi

    echo -e "\n${C_BOLD}Scanning target ${C_GREEN}${target}${C_RESET} across ${#port_list[@]} ports:${C_RESET}\n"
    printf "%-10s | %-10s | %s\n" "PORT" "STATUS" "SERVICE"
    echo -e "----------------------------------------------"

    for p in "${port_list[@]}"; do
        # Test TCP connection using bash /dev/tcp
        if (exec 3<>/dev/tcp/"$target"/"$p") 2>/dev/null; then
            exec 3<&-
            exec 3>&-
            printf "${C_GREEN}%-10s${C_RESET} | ${C_GREEN}%-10s${C_RESET} | %s\n" "${p}/tcp" "OPEN" "Port $p"
        elif command -v nc >/dev/null 2>&1 && nc -z -w 1 "$target" "$p" 2>/dev/null; then
            printf "${C_GREEN}%-10s${C_RESET} | ${C_GREEN}%-10s${C_RESET} | %s\n" "${p}/tcp" "OPEN" "Port $p"
        fi
    done
    echo -e "----------------------------------------------\n"
}

# Run Nmap Scan Mode
run_nmap_scan() {
    local target="$1"
    local ports="$2"
    local extra="$3"

    if ! command -v nmap >/dev/null 2>&1; then
        echo -e "${C_RED}[!] Nmap is not installed.${C_RESET}"
        read -rp "Would you like to install nmap now? (y/n): " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            install_dependencies
        else
            return
        fi
    fi

    echo -e "\n${C_CYAN}[*] Running Nmap on ${target}...${C_RESET}\n"
    local nmap_cmd="nmap"
    [ "$IS_ROOT" = true ] || [ "$IS_KALI" = true ] && nmap_cmd="sudo nmap"

    local port_flag=""
    if [ -n "$ports" ] && [ "$ports" != "top100" ]; then
        if [ "$ports" = "top20" ]; then
            port_flag="--top-ports 20"
        elif [ "$ports" = "top1000" ]; then
            port_flag="--top-ports 1000"
        elif [ "$ports" = "all" ]; then
            port_flag="-p-"
        else
            port_flag="-p $ports"
        fi
    else
        port_flag="-F"
    fi

    $nmap_cmd -sV $port_flag $extra "$target"
}

# Interactive Menu UI
interactive_menu() {
    while true; do
        clear
        print_banner
        echo -e "${C_BOLD}MAIN MENU:${C_RESET}\n"
        echo -e "  ${C_CYAN}[1]${C_RESET}  Fast TCP Port Scanner (Top Ports / Range / Full)"
        echo -e "  ${C_CYAN}[2]${C_RESET}  Deep Service & Banner Detector (Fingerprint / HTTP / SSL)"
        echo -e "  ${C_CYAN}[3]${C_RESET}  UDP Port Scanner (DNS, NTP, SNMP, DHCP, etc.)"
        echo -e "  ${C_CYAN}[4]${C_RESET}  Local Port Inspector (View Active Listening Sockets & PIDs)"
        echo -e "  ${C_CYAN}[5]${C_RESET}  Kill Process on Port (Free up occupied port)"
        echo -e "  ${C_CYAN}[6]${C_RESET}  Port Listener / Reverse Shell Catcher (Netcat Mode)"
        echo -e "  ${C_CYAN}[7]${C_RESET}  Port Honeypot & Intrusion Monitor (Detect & Log Attacks)"
        echo -e "  ${C_CYAN}[8]${C_RESET}  TCP Port Forwarder / Relay Proxy (Local -> Remote)"
        echo -e "  ${C_CYAN}[9]${C_RESET}  Firewall Outbound Egress Checker (Find Blocked Ports)"
        echo -e "  ${C_CYAN}[10]${C_RESET} Network Interfaces & Public IP Lookup"
        echo -e "  ${C_CYAN}[11]${C_RESET} Port Knowledgebase & Vulnerability Directory (Search 200+ Ports)"
        echo -e "  ${C_CYAN}[12]${C_RESET} Nmap Advanced Scan Integration"
        echo -e "  ${C_CYAN}[13]${C_RESET} Install / Update Dependencies (Kali & Termux)"
        echo -e "  ${C_RED}[0]${C_RESET}  Exit\n"

        read -rp "Select an option [0-13]: " choice
        case "$choice" in
            1)
                echo -e "\n${C_BOLD}--- Fast TCP Port Scanner ---${C_RESET}"
                read -rp "Enter target host/IP (e.g. 127.0.0.1 or scanme.org): " t_host
                [ -z "$t_host" ] && continue
                echo -e "Port choices: ${C_YELLOW}top20${C_RESET}, ${C_YELLOW}top100${C_RESET}, ${C_YELLOW}top1000${C_RESET}, ${C_YELLOW}wellknown${C_RESET}, ${C_YELLOW}all${C_RESET}, or custom (e.g. 80,443,8000-8080)"
                read -rp "Enter ports [default: top100]: " t_ports
                [ -z "$t_ports" ] && t_ports="top100"
                read -rp "Export report? Enter filename (.txt, .json, .csv, .html) or press Enter to skip: " t_out
                
                out_arg=()
                [ -n "$t_out" ] && out_arg=("-o" "$t_out")

                if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                    $PYTHON_CMD "$ENGINE_PATH" scan -t "$t_host" -p "$t_ports" -m fast "${out_arg[@]}"
                else
                    run_bash_port_scan "$t_host" "$t_ports"
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            2)
                echo -e "\n${C_BOLD}--- Deep Service & Banner Detection ---${C_RESET}"
                read -rp "Enter target host/IP: " t_host
                [ -z "$t_host" ] && continue
                echo -e "Port choices: ${C_YELLOW}top20${C_RESET}, ${C_YELLOW}top100${C_RESET}, custom (e.g. 21,22,80,443,3306,6379,8080)"
                read -rp "Enter ports [default: top20]: " t_ports
                [ -z "$t_ports" ] && t_ports="top20"
                read -rp "Generate modern HTML report? (y/n) [default: y]: " want_html
                out_arg=()
                if [[ ! "$want_html" =~ ^[Nn]$ ]]; then
                    rep_name="$REPORTS_DIR/scan_${t_host}_$(date +%Y%m%d_%H%M%S).html"
                    out_arg=("-o" "$rep_name")
                fi

                if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                    $PYTHON_CMD "$ENGINE_PATH" scan -t "$t_host" -p "$t_ports" -m deep "${out_arg[@]}"
                else
                    run_bash_port_scan "$t_host" "$t_ports"
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            3)
                echo -e "\n${C_BOLD}--- UDP Port Scanner ---${C_RESET}"
                read -rp "Enter target host/IP: " t_host
                [ -z "$t_host" ] && continue
                read -rp "Enter UDP ports [default: 53,67,68,69,123,161,162,500,514,1194,1900,5353]: " t_ports
                [ -z "$t_ports" ] && t_ports="53,67,68,69,123,161,162,500,514,1194,1900,5353"

                if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                    $PYTHON_CMD "$ENGINE_PATH" scan -t "$t_host" -p "$t_ports" -m udp
                else
                    echo -e "${C_RED}[!] Python required for UDP probe engine.${C_RESET}"
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            4)
                echo -e "\n${C_BOLD}--- Local Port Inspector ---${C_RESET}"
                if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                    $PYTHON_CMD "$ENGINE_PATH" inspect
                else
                    command -v ss >/dev/null 2>&1 && ss -tulnp || netstat -tulnp
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            5)
                echo -e "\n${C_BOLD}--- Kill Process on Port ---${C_RESET}"
                read -rp "Enter port number to free up (e.g. 8080): " k_port
                if [ -n "$k_port" ]; then
                    if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                        $PYTHON_CMD "$ENGINE_PATH" kill -p "$k_port"
                    else
                        fuser -k "${k_port}/tcp" 2>/dev/null && echo "Killed via fuser" || echo "Failed"
                    fi
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            6)
                echo -e "\n${C_BOLD}--- Port Listener / Reverse Shell Catcher ---${C_RESET}"
                read -rp "Enter port to listen on (e.g. 4444): " l_port
                [ -z "$l_port" ] && continue
                read -rp "Protocol: (1) TCP [Default], (2) UDP: " proto_choice
                udp_flag=()
                [ "$proto_choice" = "2" ] && udp_flag=("-u")
                read -rp "Save session log to file? (leave blank to skip): " l_file
                file_flag=()
                [ -n "$l_file" ] && file_flag=("-o" "$l_file")

                if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                    $PYTHON_CMD "$ENGINE_PATH" listen -p "$l_port" "${udp_flag[@]}" "${file_flag[@]}"
                elif command -v nc >/dev/null 2>&1; then
                    nc -lvnp "$l_port"
                else
                    echo -e "${C_RED}[!] No listener tool available.${C_RESET}"
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            7)
                echo -e "\n${C_BOLD}--- Port Honeypot & Intrusion Monitor ---${C_RESET}"
                read -rp "Enter port to expose as honeypot (e.g. 2222, 8080, 21): " h_port
                [ -z "$h_port" ] && continue
                echo -e "Available simulated banners: ${C_YELLOW}ssh${C_RESET}, ${C_YELLOW}ftp${C_RESET}, ${C_YELLOW}http${C_RESET}, ${C_YELLOW}smtp${C_RESET}, ${C_YELLOW}telnet${C_RESET}, ${C_YELLOW}generic${C_RESET}"
                read -rp "Select service emulation [default: generic]: " h_serv
                [ -z "$h_serv" ] && h_serv="generic"

                if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                    $PYTHON_CMD "$ENGINE_PATH" honeypot -p "$h_port" -s "$h_serv"
                else
                    echo -e "${C_RED}[!] Python required for honeypot monitor.${C_RESET}"
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            8)
                echo -e "\n${C_BOLD}--- TCP Port Forwarder / Relay Proxy ---${C_RESET}"
                read -rp "Enter local port to listen on (e.g. 8080): " lp
                read -rp "Enter remote target HOST:PORT (e.g. 192.168.1.100:80): " rp
                if [ -n "$lp" ] && [ -n "$rp" ]; then
                    if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                        $PYTHON_CMD "$ENGINE_PATH" forward -l "$lp" -r "$rp"
                    elif command -v socat >/dev/null 2>&1; then
                        socat "TCP-LISTEN:$lp,fork" "TCP:$rp"
                    else
                        echo -e "${C_RED}[!] Python or Socat required for port forwarding.${C_RESET}"
                    fi
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            9)
                echo -e "\n${C_BOLD}--- Firewall Outbound Egress Checker ---${C_RESET}"
                if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                    $PYTHON_CMD "$ENGINE_PATH" egress
                else
                    echo -e "${C_RED}[!] Python required for multi-threaded egress testing.${C_RESET}"
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            10)
                show_ip_info
                read -rp "Press Enter to return to menu..."
                ;;

            11)
                echo -e "\n${C_BOLD}--- Port Knowledgebase & Vulnerability Directory ---${C_RESET}"
                read -rp "Enter port number or service keyword (e.g. 445, 3389, ssh, database): " q
                if [ -n "$q" ]; then
                    if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                        $PYTHON_CMD "$ENGINE_PATH" lookup "$q"
                    else
                        grep -i "$q" "$CORE_DIR/ports_db.json" 2>/dev/null || echo "No match"
                    fi
                fi
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            12)
                echo -e "\n${C_BOLD}--- Nmap Integration ---${C_RESET}"
                read -rp "Enter target host/IP: " n_target
                [ -z "$n_target" ] && continue
                read -rp "Enter ports [default: top100]: " n_ports
                read -rp "Additional Nmap flags (e.g. -A, -sS, -Pn, -T4) [optional]: " n_extra
                run_nmap_scan "$n_target" "$n_ports" "$n_extra"
                echo ""
                read -rp "Press Enter to return to menu..."
                ;;

            13)
                install_dependencies
                read -rp "Press Enter to return to menu..."
                ;;

            0)
                echo -e "\n${C_CYAN}[*] Thank you for using Port Tool. Stay safe!${C_RESET}\n"
                exit 0
                ;;

            *)
                echo -e "${C_RED}[!] Invalid option. Please choose between 0 and 13.${C_RESET}"
                sleep 1
                ;;
        esac
    done
}

# CLI Argument Parser (Non-interactive execution)
parse_cli() {
    TARGET=""
    PORTS="top100"
    MODE="fast"
    THREADS=100
    TIMEOUT=1.5
    OUTPUT=""
    DO_INSPECT=false
    KILL_PORT=""
    KILL_FORCE=false
    LISTEN_PORT=""
    IS_UDP=false
    HONEYPOT_PORT=""
    HONEYPOT_SERVICE="generic"
    FORWARD_SPEC=""
    DO_EGRESS=false
    LOOKUP_QUERY=""
    DO_IP=false
    DO_INSTALL=false

    while [ $# -gt 0 ]; do
        case "$1" in
            -t|--target)
                TARGET="$2"
                shift 2
                ;;
            -p|--ports)
                PORTS="$2"
                shift 2
                ;;
            -m|--mode)
                MODE="$2"
                shift 2
                ;;
            -T|--threads)
                THREADS="$2"
                shift 2
                ;;
            -W|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT="$2"
                shift 2
                ;;
            -i|--inspect)
                DO_INSPECT=true
                shift
                ;;
            -k|--kill)
                KILL_PORT="$2"
                shift 2
                ;;
            --force)
                KILL_FORCE=true
                shift
                ;;
            -l|--listen)
                LISTEN_PORT="$2"
                shift 2
                ;;
            -u|--udp)
                IS_UDP=true
                shift
                ;;
            --honeypot)
                HONEYPOT_PORT="$2"
                shift 2
                ;;
            --service)
                HONEYPOT_SERVICE="$2"
                shift 2
                ;;
            -f|--forward)
                FORWARD_SPEC="$2"
                shift 2
                ;;
            -e|--egress)
                DO_EGRESS=true
                shift
                ;;
            -q|--lookup)
                LOOKUP_QUERY="$2"
                shift 2
                ;;
            --ip)
                DO_IP=true
                shift
                ;;
            --install|--setup)
                DO_INSTALL=true
                shift
                ;;
            --no-color)
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "Port Tool v${APP_VERSION} (${OS_NAME})"
                exit 0
                ;;
            *)
                echo -e "${C_RED}[!] Unknown argument: $1${C_RESET}"
                echo "Use ./port.sh --help for usage instructions."
                exit 1
                ;;
        esac
    done

    # Execute specific actions based on flags
    if [ "$DO_INSTALL" = true ]; then
        install_dependencies
        exit 0
    fi

    if [ "$DO_IP" = true ]; then
        show_ip_info
        exit 0
    fi

    if [ "$DO_INSPECT" = true ]; then
        if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
            $PYTHON_CMD "$ENGINE_PATH" inspect
        else
            ss -tulnp 2>/dev/null || netstat -tulnp
        fi
        exit 0
    fi

    if [ -n "$KILL_PORT" ]; then
        force_flag=()
        [ "$KILL_FORCE" = true ] && force_flag=("-f")
        if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
            $PYTHON_CMD "$ENGINE_PATH" kill -p "$KILL_PORT" "${force_flag[@]}"
        else
            fuser -k "${KILL_PORT}/tcp" 2>/dev/null && echo "Killed port $KILL_PORT"
        fi
        exit 0
    fi

    if [ -n "$LISTEN_PORT" ]; then
        udp_arg=()
        [ "$IS_UDP" = true ] && udp_arg=("-u")
        out_arg=()
        [ -n "$OUTPUT" ] && out_arg=("-o" "$OUTPUT")
        if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
            $PYTHON_CMD "$ENGINE_PATH" listen -p "$LISTEN_PORT" "${udp_arg[@]}" "${out_arg[@]}"
        elif command -v nc >/dev/null 2>&1; then
            nc -lvnp "$LISTEN_PORT"
        fi
        exit 0
    fi

    if [ -n "$HONEYPOT_PORT" ]; then
        if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
            $PYTHON_CMD "$ENGINE_PATH" honeypot -p "$HONEYPOT_PORT" -s "$HONEYPOT_SERVICE"
        else
            echo -e "${C_RED}[!] Python required for honeypot.${C_RESET}"
            exit 1
        fi
        exit 0
    fi

    if [ -n "$FORWARD_SPEC" ]; then
        if [[ "$FORWARD_SPEC" =~ ^([0-9]+):([^:]+):([0-9]+)$ ]]; then
            lport="${BASH_REMATCH[1]}"
            rhost="${BASH_REMATCH[2]}"
            rport="${BASH_REMATCH[3]}"
            if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
                $PYTHON_CMD "$ENGINE_PATH" forward -l "$lport" -r "${rhost}:${rport}"
            elif command -v socat >/dev/null 2>&1; then
                socat "TCP-LISTEN:$lport,fork" "TCP:$rhost:$rport"
            fi
            exit 0
        else
            echo -e "${C_RED}[!] Invalid forward format. Expected: <lport>:<rhost>:<rport> (e.g. 8080:192.168.1.1:80)${C_RESET}"
            exit 1
        fi
    fi

    if [ "$DO_EGRESS" = true ]; then
        if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
            $PYTHON_CMD "$ENGINE_PATH" egress
        else
            echo -e "${C_RED}[!] Python required for egress check.${C_RESET}"
            exit 1
        fi
        exit 0
    fi

    if [ -n "$LOOKUP_QUERY" ]; then
        if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
            $PYTHON_CMD "$ENGINE_PATH" lookup "$LOOKUP_QUERY"
        else
            grep -i "$LOOKUP_QUERY" "$CORE_DIR/ports_db.json"
        fi
        exit 0
    fi

    # Target scan
    if [ -n "$TARGET" ]; then
        print_banner
        if [ "$MODE" = "nmap" ] || [ "$MODE" = "syn" ]; then
            extra_flag=""
            [ "$MODE" = "syn" ] && extra_flag="-sS"
            run_nmap_scan "$TARGET" "$PORTS" "$extra_flag"
            exit 0
        fi

        out_arg=()
        [ -n "$OUTPUT" ] && out_arg=("-o" "$OUTPUT")

        if [ -n "$PYTHON_CMD" ] && [ -n "$ENGINE_PATH" ]; then
            $PYTHON_CMD "$ENGINE_PATH" scan -t "$TARGET" -p "$PORTS" -m "$MODE" -T "$THREADS" -W "$TIMEOUT" "${out_arg[@]}"
        else
            run_bash_port_scan "$TARGET" "$PORTS"
        fi
        exit 0
    fi

    # If no flags given, launch interactive menu
    interactive_menu
}

# Entrypoint
if [ $# -eq 0 ]; then
    interactive_menu
else
    parse_cli "$@"
fi
