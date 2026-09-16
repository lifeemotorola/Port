#!/usr/bin/env python3
"""
Port Guide & Playbook Assistant
Generates step-by-step next action guides for Kali Linux and Termux
Part of Port - Advance Internet Port Tool
"""

import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(BASE_DIR, "core")
PLAYBOOKS_FILE = os.path.join(CORE_DIR, "playbooks.json")

# ANSI Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[0;31m"
C_GREEN = "\033[0;32m"
C_YELLOW = "\033[1;33m"
C_BLUE = "\033[0;34m"
C_PURPLE = "\033[0;35m"
C_CYAN = "\033[0;36m"
C_WHITE = "\033[1;37m"
C_GRAY = "\033[0;90m"
C_BG_BLUE = "\033[44m\033[37m"

if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
    C_RESET = C_BOLD = C_RED = C_GREEN = C_YELLOW = C_BLUE = C_PURPLE = C_CYAN = C_WHITE = C_GRAY = C_BG_BLUE = ""

PLAYBOOKS_CACHE = {}

def load_playbooks():
    global PLAYBOOKS_CACHE
    if not PLAYBOOKS_CACHE and os.path.exists(PLAYBOOKS_FILE):
        try:
            with open(PLAYBOOKS_FILE, "r", encoding="utf-8") as f:
                PLAYBOOKS_CACHE = json.load(f)
        except Exception:
            pass
    return PLAYBOOKS_CACHE

# Service to Port mapping fallbacks
SERVICE_MAP = {
    "ftp": "21",
    "ssh": "22",
    "telnet": "23",
    "smtp": "25",
    "smtps": "25",
    "dns": "53",
    "domain": "53",
    "http": "80",
    "www": "80",
    "https": "443",
    "ssl": "443",
    "smb": "445",
    "microsoft-ds": "445",
    "netbios": "445",
    "mssql": "1433",
    "ms-sql-s": "1433",
    "nfs": "2049",
    "docker": "2375",
    "mysql": "3306",
    "mariadb": "3306",
    "rdp": "3389",
    "ms-wbt-server": "3389",
    "postgres": "5432",
    "postgresql": "5432",
    "vnc": "5900",
    "redis": "6379",
    "tomcat": "8080",
    "http-proxy": "8080",
    "elasticsearch": "9200",
    "elastic": "9200",
    "webmin": "10000",
    "mongodb": "27017"
}

def get_generic_playbook(port, service_name="unknown"):
    return {
        "service": f"{service_name.upper()} (Port {port})",
        "summary": f"Service '{service_name}' identified on port {port}. Follow standard reconnaissance, protocol analysis, and vulnerability probing methodology.",
        "risk": "Medium" if int(port) < 1024 else "Low",
        "steps": [
            {
                "step": 1,
                "title": "Raw Banner Grabbing & Handshake Identification",
                "desc": "Connect to receive the service's initial greeting string and protocol identifier.",
                "kali_cmd": f"nc -nv <target> {port} || openssl s_client -connect <target>:{port}",
                "termux_cmd": f"nc -nv <target> {port}",
                "indicator": "Printable daemon version string or protocol identification header."
            },
            {
                "step": 2,
                "title": "Nmap Deep Service & Default Script Scan",
                "desc": "Run Nmap version detection and automated NSE scripts against this specific port.",
                "kali_cmd": f"nmap -p {port} -sV -sC <target>",
                "termux_cmd": f"nmap -p {port} -sV <target>",
                "indicator": "Exact software name, version number, OS CPE, and NSE script output."
            },
            {
                "step": 3,
                "title": "Search for Known CVEs & Exploits",
                "desc": "Check Exploit-DB / SearchSploit for disclosed vulnerabilities matching the discovered software version.",
                "kali_cmd": "searchsploit <service_version>",
                "termux_cmd": "curl -s 'https://api.cvedetails.com' || searchsploit <service_version>",
                "indicator": "Remote code execution, authentication bypass, or denial of service exploits."
            },
            {
                "step": 4,
                "title": "Credential Auditing / Password Guessing",
                "desc": "If an authentication mechanism is exposed, test for default or weak credentials.",
                "kali_cmd": f"hydra -L users.txt -P passwords.txt <target> -s {port} <service>",
                "termux_cmd": f"hydra -l admin -P passwords.txt <target> -s {port}",
                "indicator": "Valid credentials discovered."
            }
        ]
    }

def get_playbook_for_port(port, service_name=None):
    load_playbooks()
    q_str = str(port).strip().lower()

    # Match by query keyword in SERVICE_MAP (e.g. 'redis' -> 6379, 'smb' -> 445)
    for k, p_key in SERVICE_MAP.items():
        if k in q_str:
            if p_key in PLAYBOOKS_CACHE:
                return PLAYBOOKS_CACHE[p_key]

    # Direct match by port number
    if q_str.isdigit() and q_str in PLAYBOOKS_CACHE:
        return PLAYBOOKS_CACHE[q_str]

    # Match by service_name if provided
    if service_name:
        s_norm = str(service_name).lower().strip()
        for k, p_key in SERVICE_MAP.items():
            if k in s_norm:
                if p_key in PLAYBOOKS_CACHE:
                    return PLAYBOOKS_CACHE[p_key]

    port_val = int(q_str) if q_str.isdigit() else 80
    return get_generic_playbook(port_val, service_name or q_str)

def interpolate(text, target, port, target_domain="example.com"):
    if not text:
        return ""
    res = text.replace("<target>", str(target))
    res = res.replace("<port>", str(port))
    res = res.replace("<target_domain>", str(target_domain))
    res = res.replace("<service_version>", "service_name_here")
    return res

def format_playbook_cli(playbook, target="<target>", port=None, is_termux=False):
    """Format step-by-step guide with ANSI colors for terminal output"""
    port_val = port or "PORT"
    if port and not str(port).isdigit():
        for k, p_key in SERVICE_MAP.items():
            if k in str(port).lower():
                port_val = p_key
                break

    risk = playbook.get("risk", "Medium")
    risk_color = {
        "Critical": C_RED + C_BOLD,
        "High": C_RED,
        "Medium": C_YELLOW,
        "Low": C_GREEN,
        "Informational": C_CYAN
    }.get(risk, C_WHITE)

    lines = []
    lines.append(f"\n{C_PURPLE}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    lines.append(f"{C_PURPLE}{C_BOLD}║  🎯 STEP-BY-STEP PLAYBOOK: {C_WHITE}{playbook.get('service', 'Service')} [Port {port_val}]{C_PURPLE}{C_BOLD}  ║{C_RESET}")
    lines.append(f"{C_PURPLE}{C_BOLD}╚══════════════════════════════════════════════════════════════════════════════╝{C_RESET}")
    lines.append(f"  {C_BOLD}Risk Level  :{C_RESET} {risk_color}{risk}{C_RESET}")
    lines.append(f"  {C_BOLD}Overview    :{C_RESET} {C_GRAY}{playbook.get('summary', '')}{C_RESET}\n")

    steps = playbook.get("steps", [])
    for s in steps:
        step_num = s.get("step", 1)
        title = s.get("title", "")
        desc = s.get("desc", "")
        kali_cmd = interpolate(s.get("kali_cmd", ""), target, port_val)
        termux_cmd = interpolate(s.get("termux_cmd", ""), target, port_val)
        indicator = s.get("indicator", "")

        lines.append(f"  {C_CYAN}{C_BOLD}▶ STEP {step_num}: {title}{C_RESET}")
        lines.append(f"    {C_GRAY}{desc}{C_RESET}\n")

        if is_termux:
            lines.append(f"    {C_GREEN}{C_BOLD}[Termux Command]:{C_RESET}")
            lines.append(f"    {C_WHITE}  $ {termux_cmd}{C_RESET}\n")
            lines.append(f"    {C_BLUE}{C_BOLD}[Kali Linux Alternative]:{C_RESET}")
            lines.append(f"    {C_GRAY}  $ {kali_cmd}{C_RESET}\n")
        else:
            lines.append(f"    {C_BLUE}{C_BOLD}[Kali Linux Command]:{C_RESET}")
            lines.append(f"    {C_WHITE}  $ {kali_cmd}{C_RESET}\n")
            lines.append(f"    {C_GREEN}{C_BOLD}[Termux Alternative]:{C_RESET}")
            lines.append(f"    {C_GRAY}  $ {termux_cmd}{C_RESET}\n")

        if indicator:
            lines.append(f"    {C_YELLOW}{C_BOLD}✔ What to Look For:{C_RESET} {indicator}\n")
        lines.append(f"  {C_GRAY}────────────────────────────────────────────────────────────────────────{C_RESET}")

    return "\n".join(lines)

def print_playbook_cli(port, target="<target>", service_name=None, is_termux=False):
    playbook = get_playbook_for_port(port, service_name)
    print(format_playbook_cli(playbook, target=target, port=port, is_termux=is_termux))

def get_playbook_html_section(open_ports, target="<target>"):
    """Generate HTML section with interactive step-by-step accordion for each open port"""
    if not open_ports:
        return ""

    cards_html = []
    for p in open_ports:
        port_num = p["port"]
        serv = p.get("service", "unknown")
        playbook = get_playbook_for_port(port_num, serv)
        risk = playbook.get("risk", "Medium")

        risk_color = {
            "Critical": "#ff3860",
            "High": "#ff7979",
            "Medium": "#ffdd57",
            "Low": "#48c774",
            "Informational": "#209cee"
        }.get(risk, "#7957d5")

        steps_html = []
        for s in playbook.get("steps", []):
            kali_cmd = interpolate(s.get("kali_cmd", ""), target, port_num)
            termux_cmd = interpolate(s.get("termux_cmd", ""), target, port_num)
            steps_html.append(f"""
            <div class="guide-step">
                <div class="step-header">
                    <span class="step-num">Step {s.get('step')}</span>
                    <strong>{s.get('title')}</strong>
                </div>
                <div class="step-desc">{s.get('desc')}</div>
                <div class="cmd-block">
                    <div class="cmd-label kali-label">Kali Linux:</div>
                    <code>{kali_cmd}</code>
                </div>
                <div class="cmd-block">
                    <div class="cmd-label termux-label">Termux:</div>
                    <code>{termux_cmd}</code>
                </div>
                <div class="indicator-box">
                    <strong>✔ Expected Indicator:</strong> {s.get('indicator', '')}
                </div>
            </div>
            """)

        cards_html.append(f"""
        <div class="guide-card">
            <div class="guide-card-header" onclick="toggleGuide('guide_{port_num}')">
                <div>
                    <span class="guide-port-pill">{port_num} / {p.get('proto', 'tcp')}</span>
                    <strong style="margin-left: 8px; font-size: 16px;">{playbook.get('service')}</strong>
                    <span class="tag" style="background:{risk_color}; color:#0a0a0a; margin-left: 10px;">{risk}</span>
                </div>
                <div class="toggle-icon">▼ Click to Expand Step-by-Step Playbook</div>
            </div>
            <div id="guide_{port_num}" class="guide-body" style="display: block;">
                <p class="guide-summary">{playbook.get('summary')}</p>
                <div class="steps-container">
                    {"".join(steps_html)}
                </div>
            </div>
        </div>
        """)

    return f"""
    <div class="guide-section">
        <h2 style="color:var(--accent); font-size:20px; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-top: 36px;">
            🎯 Step-by-Step Security Assessment & Penetration Testing Playbooks
        </h2>
        <p style="color:#94a3b8; font-size:14px; margin-bottom: 20px;">
            Recommended sequential action steps and copy-paste commands for each open port identified during the scan:
        </p>
        {"".join(cards_html)}
    </div>
    """

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port_query = sys.argv[1]
        target_host = sys.argv[2] if len(sys.argv) > 2 else "<target>"
        is_t = ("TERMUX_VERSION" in os.environ)
        print_playbook_cli(port_query, target=target_host, is_termux=is_t)
    else:
        print("Usage: python3 guide.py <port> [target]")
