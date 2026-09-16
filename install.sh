#!/usr/bin/env bash
# ==============================================================================
# Installer for Port - Advance Internet Port Tool
# Specialized for Kali Linux & Termux
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ANSI Colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_RED="\033[0;31m"
C_GREEN="\033[0;32m"
C_YELLOW="\033[1;33m"
C_CYAN="\033[0;36m"
C_GRAY="\033[0;90m"

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
echo -e "   ${C_BOLD}Installing Port - Advance Internet Port Tool${C_RESET}"
echo -e "   ${C_GRAY}===================================================${C_RESET}\n"

# Environment Detection
IS_TERMUX=false
IS_ROOT=false
[ "$(id -u)" -eq 0 ] && IS_ROOT=true

if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ] || [[ "$PREFIX" == *"com.termux"* ]]; then
    IS_TERMUX=true
    OS_NAME="Termux (Android)"
    BIN_DIR="${PREFIX:-/data/data/com.termux/files/usr}/bin"
    OPT_DIR="${PREFIX:-/data/data/com.termux/files/usr}/opt/port"
else
    if [ -f "/etc/os-release" ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        OS_NAME="${PRETTY_NAME:-Linux}"
    else
        OS_NAME="Linux"
    fi
    BIN_DIR="/usr/local/bin"
    OPT_DIR="/opt/port"
fi

echo -e "${C_CYAN}[*] Detected Environment:${C_RESET} ${C_BOLD}${OS_NAME}${C_RESET}"
echo -e "${C_CYAN}[*] Target Binary Directory:${C_RESET} ${BIN_DIR}"
echo -e "${C_CYAN}[*] Target Library Directory:${C_RESET} ${OPT_DIR}\n"

# Check & Install Package Dependencies
echo -e "${C_YELLOW}[*] Installing required packages...${C_RESET}"
if [ "$IS_TERMUX" = true ]; then
    echo -e "${C_GRAY}Running pkg install...${C_RESET}"
    pkg update -y || apt update -y
    pkg install -y python curl netcat-openbsd socat dnsutils jq nmap || true
elif [ "$IS_ROOT" = true ]; then
    echo -e "${C_GRAY}Running apt-get install (root)...${C_RESET}"
    apt-get update -y && apt-get install -y python3 curl netcat-traditional socat dnsutils jq nmap iproute2 || true
else
    echo -e "${C_GRAY}Running sudo apt-get install...${C_RESET}"
    sudo apt-get update -y && sudo apt-get install -y python3 curl netcat-traditional socat dnsutils jq nmap iproute2 || true
fi

# Set executable permissions
chmod +x "$SCRIPT_DIR/port.sh"
chmod +x "$SCRIPT_DIR/core/engine.py" "$SCRIPT_DIR/core/guide.py" 2>/dev/null || true

# Deploy to OPT_DIR and create BIN symlink
echo -e "\n${C_CYAN}[*] Setting up application files...${C_RESET}"

if [ "$IS_TERMUX" = true ]; then
    mkdir -p "$OPT_DIR"
    cp -r "$SCRIPT_DIR"/* "$OPT_DIR/" 2>/dev/null || true
    chmod +x "$OPT_DIR/port.sh" "$OPT_DIR/core/engine.py" "$OPT_DIR/core/guide.py" 2>/dev/null || true
    ln -sf "$OPT_DIR/port.sh" "$BIN_DIR/port"
elif [ "$IS_ROOT" = true ]; then
    mkdir -p "$OPT_DIR"
    cp -r "$SCRIPT_DIR"/* "$OPT_DIR/" 2>/dev/null || true
    chmod +x "$OPT_DIR/port.sh" "$OPT_DIR/core/engine.py" "$OPT_DIR/core/guide.py" 2>/dev/null || true
    ln -sf "$OPT_DIR/port.sh" "$BIN_DIR/port"
else
    # Non-root linux
    if sudo mkdir -p "$OPT_DIR" 2>/dev/null; then
        sudo cp -r "$SCRIPT_DIR"/* "$OPT_DIR/"
        sudo chmod +x "$OPT_DIR/port.sh" "$OPT_DIR/core/engine.py" "$OPT_DIR/core/guide.py"
        sudo ln -sf "$OPT_DIR/port.sh" "$BIN_DIR/port"
    else
        # Fallback to user local link
        mkdir -p "$HOME/.local/bin"
        ln -sf "$SCRIPT_DIR/port.sh" "$HOME/.local/bin/port"
        echo -e "${C_YELLOW}[!] Notice: Created symlink in $HOME/.local/bin/port. Ensure $HOME/.local/bin is in your PATH.${C_RESET}"
    fi
fi

echo -e "\n${C_GREEN}${C_BOLD}[✓] Port tool installed successfully!${C_RESET}\n"
echo -e "You can now run ${C_CYAN}${C_BOLD}port${C_RESET} from any directory in your terminal:"
echo -e "  ${C_WHITE}port${C_RESET}                          Launch interactive menu"
echo -e "  ${C_WHITE}port -t <target> -p top100${C_RESET}    Scan remote target"
echo -e "  ${C_WHITE}port -t <target> --guide${C_RESET}      Scan target and get step-by-step playbooks"
echo -e "  ${C_WHITE}port -g 445${C_RESET}                   Step-by-step action guide for port 445"
echo -e "  ${C_WHITE}port -i${C_RESET}                       Inspect local listening ports"
echo -e "  ${C_WHITE}port -k 8080${C_RESET}                  Kill process on port 8080"
echo -e "  ${C_WHITE}port -q 445${C_RESET}                   Lookup port knowledge base"
echo -e "  ${C_WHITE}port --help${C_RESET}                   Show full CLI options\n"
echo -e "${C_GRAY}Reference: https://termux.achik.us/${C_RESET}\n"
