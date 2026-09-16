#!/usr/bin/env python3
"""
Port Engine - Advanced Networking & Security Engine
Kali Linux & Termux Compatible
Part of Port - Advanced Internet Port Tool
"""

import sys
import os
import socket
import select
import ssl
import time
import json
import csv
import re
import argparse
import threading
import concurrent.futures
from datetime import datetime

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(BASE_DIR, "core")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

for d in [LOGS_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

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

# Disable colors if requested or in NO_COLOR
if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
    C_RESET = C_BOLD = C_RED = C_GREEN = C_YELLOW = C_BLUE = C_PURPLE = C_CYAN = C_WHITE = C_GRAY = ""

# Load Knowledge Base
DB_PATH = os.path.join(CORE_DIR, "ports_db.json")
PORTS_DB = {}
if os.path.exists(DB_PATH):
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            for item in json.load(f):
                PORTS_DB[int(item["port"])] = item
    except Exception:
        pass

# Top Port Presets
TOP_20_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]

TOP_100_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 79, 80, 88, 110, 111, 119, 123, 135, 137, 138, 139,
    143, 161, 162, 179, 389, 443, 445, 465, 500, 514, 515, 520, 587, 631, 636, 873, 902, 990,
    993, 995, 1080, 1194, 1433, 1434, 1521, 1720, 1723, 1883, 1900, 2049, 2082, 2083, 2181, 2222,
    2375, 2376, 2379, 3000, 3128, 3306, 3389, 4000, 4443, 4444, 4500, 5000, 5060, 5061, 5432, 5672,
    5900, 5901, 5984, 5985, 5986, 6000, 6379, 6443, 6667, 7001, 8000, 8008, 8080, 8081, 8443, 8500,
    8888, 9000, 9042, 9090, 9092, 9100, 9200, 9300, 10000, 11211, 15672, 27017, 28017, 50000
]

# Top 1000 Port Generator: includes top 100 plus 900 most common services
TOP_1000_PORTS = list(dict.fromkeys(TOP_100_PORTS + list(range(1, 1025)) + [
    1080, 1194, 1248, 1433, 1434, 1521, 1720, 1723, 1741, 1883, 1900, 1935, 1936, 1984, 2000, 2001,
    2049, 2082, 2083, 2086, 2087, 2181, 2222, 2375, 2376, 2379, 2380, 2483, 2484, 3000, 3050, 3128,
    3268, 3269, 3306, 3389, 3478, 3690, 4000, 4040, 4242, 4369, 4443, 4444, 4500, 4505, 4506, 4646,
    4647, 5000, 5001, 5060, 5061, 5182, 5222, 5269, 5353, 5432, 5554, 5555, 5556, 5672, 5683, 5684,
    5900, 5901, 5902, 5903, 5984, 5985, 5986, 6000, 6001, 6081, 6082, 6379, 6432, 6443, 6667, 6881,
    7000, 7001, 7077, 7474, 7687, 7777, 8000, 8006, 8008, 8080, 8081, 8086, 8088, 8089, 8111, 8123,
    8200, 8291, 8388, 8443, 8500, 8501, 8880, 8883, 8888, 9000, 9001, 9042, 9050, 9051, 9090, 9092,
    9100, 9200, 9300, 9418, 9443, 9870, 9997, 9999, 10000, 10001, 10086, 10250, 11211, 12201, 12345,
    15672, 25565, 27015, 27017, 27018, 27036, 27374, 28017, 31337, 50000, 50070, 51820
]))


# -------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------

def resolve_target(target):
    """Resolve domain or IP, returning (canonical_ip, hostname)"""
    target = target.strip()
    if target.startswith("http://"):
        target = target[7:]
    elif target.startswith("https://"):
        target = target[8:]
    if "/" in target:
        target = target.split("/")[0]
    if ":" in target and not target.startswith("["):
        # Could be host:port
        parts = target.split(":")
        if len(parts) == 2:
            target = parts[0]

    try:
        ip = socket.gethostbyname(target)
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = target
        return ip, hostname
    except Exception as e:
        return None, None


def parse_ports(port_arg):
    """Parse port string: 'top20', 'top100', 'top1000', 'all', '1-100', '80,443,8000-8080'"""
    if not port_arg:
        return TOP_100_PORTS

    arg_lower = str(port_arg).strip().lower()
    if arg_lower == "top20":
        return TOP_20_PORTS
    elif arg_lower == "top100":
        return TOP_100_PORTS
    elif arg_lower == "top1000":
        return TOP_1000_PORTS
    elif arg_lower in ["wellknown", "standard"]:
        return list(range(1, 1025))
    elif arg_lower == "all":
        return list(range(1, 65536))

    ports = set()
    parts = str(port_arg).split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            sub = part.split("-")
            if len(sub) == 2:
                try:
                    start, end = int(sub[0]), int(sub[1])
                    if 1 <= start <= end <= 65535:
                        ports.update(range(start, end + 1))
                except ValueError:
                    pass
        else:
            try:
                p = int(part)
                if 1 <= p <= 65535:
                    ports.add(p)
            except ValueError:
                pass
    return sorted(list(ports))


def get_port_info(port, proto="tcp"):
    """Lookup port information from knowledge base or socket.getservbyport"""
    if port in PORTS_DB:
        return PORTS_DB[port]

    serv_name = "unknown"
    try:
        serv_name = socket.getservbyport(port, proto)
    except Exception:
        pass

    return {
        "port": port,
        "proto": proto,
        "service": serv_name,
        "name": serv_name.upper() if serv_name != "unknown" else f"Port {port}",
        "desc": f"Standard {proto.upper()} service {serv_name}",
        "risk": "Medium" if port < 1024 else "Low",
        "notes": "Standard network service."
    }


# -------------------------------------------------------------
# Deep Banner Grabbing & Service Detection
# -------------------------------------------------------------

def grab_http_banner(host, port, use_ssl=False, timeout=2.0):
    """Probe HTTP/HTTPS service for status, server header, title, and SSL cert info"""
    info = {"type": "https" if use_ssl else "http", "status": None, "server": None, "title": None, "cert": None}
    try:
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_sock.settimeout(timeout)
        raw_sock.connect((host, port))

        s = raw_sock
        if use_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(raw_sock, server_hostname=host)
            try:
                cert = s.getpeercert(binary_form=False)
                if cert:
                    subj = dict(x[0] for x in cert.get("subject", ()))
                    issuer = dict(x[0] for x in cert.get("issuer", ()))
                    info["cert"] = {
                        "subject": subj.get("commonName", ""),
                        "issuer": issuer.get("organizationName", issuer.get("commonName", "")),
                        "expires": cert.get("notAfter", "")
                    }
            except Exception:
                pass

        req = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0 (Kali-Termux-PortTool/2.0)\r\nAccept: */*\r\nConnection: close\r\n\r\n"
        s.sendall(req.encode())
        resp = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            chunk = s.recv(2048)
            if not chunk:
                break
            resp += chunk
            if len(resp) > 8192:
                break
        s.close()

        text = resp.decode("utf-8", errors="ignore")
        if text.startswith("HTTP/"):
            lines = text.split("\r\n")
            info["status"] = lines[0]
            for line in lines[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip().lower()
                    if k == "server":
                        info["server"] = v.strip()
                    elif k == "x-powered-by" and not info["server"]:
                        info["server"] = v.strip()

            title_match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
            if title_match:
                info["title"] = title_match.group(1).strip()[:80]
        return info
    except Exception:
        return None


def grab_service_banner(host, port, timeout=2.0):
    """Protocol-specific deep banner grabber for SSH, FTP, SMTP, MySQL, Redis, VNC, HTTP, SSL"""
    banner_result = {
        "service": "unknown",
        "version": "",
        "banner": "",
        "ssl": None,
        "details": {}
    }

    # 1. SSL / HTTPS probe for SSL ports or 443/8443
    if port in [443, 8443, 9443, 4443, 5001, 8006, 2083, 2087]:
        http_info = grab_http_banner(host, port, use_ssl=True, timeout=timeout)
        if http_info and http_info.get("status"):
            banner_result["service"] = "https"
            banner_result["ssl"] = http_info.get("cert")
            srv = http_info.get("server") or ""
            status = http_info.get("status") or ""
            title = http_info.get("title") or ""
            banner_result["banner"] = f"{status} | Server: {srv} | Title: {title}".strip(" |")
            banner_result["version"] = srv
            return banner_result

    # 2. Redis probe (port 6379)
    if port == 6379:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.sendall(b"INFO\r\n")
            data = s.recv(1024).decode("utf-8", errors="ignore")
            s.close()
            if "redis_version" in data:
                ver = re.search(r"redis_version:([0-9\.]+)", data)
                v_str = ver.group(1) if ver else ""
                banner_result["service"] = "redis"
                banner_result["version"] = v_str
                banner_result["banner"] = f"Redis v{v_str} (UNAUTHENTICATED - CRITICAL)"
                return banner_result
            elif "NOAUTH" in data:
                banner_result["service"] = "redis"
                banner_result["banner"] = "Redis In-Memory Database (Auth Required)"
                return banner_result
        except Exception:
            pass

    # 3. MySQL / MariaDB probe (port 3306)
    if port == 3306:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            raw = s.recv(1024)
            s.close()
            if len(raw) > 5 and raw[4] == 10:  # Protocol 10
                null_pos = raw.find(b"\x00", 5)
                if null_pos != -1:
                    ver = raw[5:null_pos].decode("latin-1", errors="ignore")
                    banner_result["service"] = "mysql"
                    banner_result["version"] = ver
                    banner_result["banner"] = f"MySQL/MariaDB Protocol 10 [{ver}]"
                    return banner_result
        except Exception:
            pass

    # 4. Plain connect and read initial greeting (for SSH, FTP, SMTP, POP3, IMAP, Telnet, VNC)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))

        # Check if server sends an initial greeting immediately
        ready = select.select([s], [], [], 1.2)
        initial_banner = b""
        if ready[0]:
            initial_banner = s.recv(1024)

        if initial_banner:
            s.close()
            text = initial_banner.decode("utf-8", errors="ignore").strip()
            # Clean non-printable chars
            clean_text = "".join(c for c in text if c.isprintable() or c in "\r\n\t ").strip()

            if clean_text.startswith("SSH-"):
                banner_result["service"] = "ssh"
                banner_result["version"] = clean_text.split()[0]
                banner_result["banner"] = clean_text
                return banner_result
            elif clean_text.startswith("220"):
                if "FTP" in clean_text.upper() or port == 21:
                    banner_result["service"] = "ftp"
                else:
                    banner_result["service"] = "smtp"
                banner_result["banner"] = clean_text.splitlines()[0]
                return banner_result
            elif clean_text.startswith("+OK"):
                banner_result["service"] = "pop3"
                banner_result["banner"] = clean_text.splitlines()[0]
                return banner_result
            elif clean_text.startswith("* OK"):
                banner_result["service"] = "imap"
                banner_result["banner"] = clean_text.splitlines()[0]
                return banner_result
            elif clean_text.startswith("RFB"):
                banner_result["service"] = "vnc"
                banner_result["banner"] = f"VNC RFB {clean_text}"
                return banner_result
            else:
                banner_result["banner"] = clean_text[:120]
                return banner_result

        # If no initial greeting, try HTTP GET
        s.sendall(f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n".encode())
        http_resp = s.recv(2048).decode("utf-8", errors="ignore")
        s.close()

        if http_resp.startswith("HTTP/"):
            lines = http_resp.split("\r\n")
            status = lines[0]
            server = ""
            for l in lines[1:]:
                if l.lower().startswith("server:"):
                    server = l.split(":", 1)[1].strip()
            title_m = re.search(r"<title>(.*?)</title>", http_resp, re.IGNORECASE)
            title = title_m.group(1).strip() if title_m else ""
            banner_result["service"] = "http"
            banner_result["banner"] = f"{status} | {server} | {title}".strip(" |")
            banner_result["version"] = server
            return banner_result

    except Exception:
        pass

    # 5. Try SSL fallback
    try:
        ssl_test = grab_http_banner(host, port, use_ssl=True, timeout=timeout)
        if ssl_test and (ssl_test.get("status") or ssl_test.get("cert")):
            banner_result["service"] = "ssl/https"
            banner_result["ssl"] = ssl_test.get("cert")
            banner_result["banner"] = f"{ssl_test.get('status', '')} | {ssl_test.get('server', '')}".strip(" |")
            return banner_result
    except Exception:
        pass

    return banner_result


# -------------------------------------------------------------
# Scanner Engines
# -------------------------------------------------------------

def probe_tcp_port(host, port, timeout=1.5, deep=False):
    """Scan single TCP port, measure RTT latency, optionally grab banner"""
    start_t = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        res = s.connect_ex((host, port))
        latency_ms = round((time.time() - start_t) * 1000, 2)
        s.close()

        if res == 0:
            db_info = get_port_info(port, "tcp")
            banner_str = ""
            service_name = db_info.get("service", "unknown")
            ssl_info = None

            if deep:
                deep_info = grab_service_banner(host, port, timeout=min(timeout + 0.5, 3.0))
                if deep_info["service"] != "unknown":
                    service_name = deep_info["service"]
                banner_str = deep_info["banner"]
                ssl_info = deep_info.get("ssl")

            return {
                "port": port,
                "proto": "tcp",
                "state": "open",
                "latency_ms": latency_ms,
                "service": service_name,
                "friendly_name": db_info.get("name", ""),
                "banner": banner_str,
                "ssl": ssl_info,
                "risk": db_info.get("risk", "Low"),
                "notes": db_info.get("notes", "")
            }
        return None
    except Exception:
        try:
            s.close()
        except:
            pass
        return None


def probe_udp_port(host, port, timeout=2.0):
    """Send standard UDP probe packets for common UDP services"""
    # Probes dictionary for common UDP protocols
    PROBES = {
        53: b"\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07version\x04bind\x00\x00\x10\x00\x03",  # DNS query
        123: b"\x1b" + 47 * b"\0",  # NTP v3
        161: b"\x30\x29\x02\x01\x01\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x1c\x02\x04\x00\x00\x00\x00\x02\x01\x00\x02\x01\x00\x30\x0e\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00",  # SNMP v2c public
        1900: b"M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n"
    }

    probe = PROBES.get(port, b"\x00" * 4)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    start_t = time.time()
    try:
        s.sendto(probe, (host, port))
        data, addr = s.recvfrom(2048)
        latency_ms = round((time.time() - start_t) * 1000, 2)
        s.close()

        db_info = get_port_info(port, "udp")
        banner = "".join(c for c in data.decode("utf-8", errors="ignore") if c.isprintable())[:100]
        return {
            "port": port,
            "proto": "udp",
            "state": "open",
            "latency_ms": latency_ms,
            "service": db_info.get("service", "unknown"),
            "friendly_name": db_info.get("name", ""),
            "banner": banner or f"UDP response ({len(data)} bytes)",
            "risk": db_info.get("risk", "Low"),
            "notes": db_info.get("notes", "")
        }
    except socket.timeout:
        s.close()
        return None
    except Exception:
        s.close()
        return None


def run_port_scan(target, ports, mode="fast", threads=100, timeout=1.5, progress_cb=None):
    """Execute multi-threaded scan across list of ports"""
    ip, hostname = resolve_target(target)
    if not ip:
        return {"error": f"Failed to resolve target: {target}"}

    start_time = time.time()
    scan_results = []
    deep_mode = (mode == "deep")
    is_udp = (mode == "udp")

    total_ports = len(ports)
    completed = 0

    scan_func = probe_udp_port if is_udp else lambda p: probe_tcp_port(ip, p, timeout=timeout, deep=deep_mode)

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(threads, total_ports or 1)) as executor:
        future_map = {executor.submit(scan_func, p): p for p in ports}
        for future in concurrent.futures.as_completed(future_map):
            completed += 1
            if progress_cb:
                progress_cb(completed, total_ports)
            try:
                res = future.result()
                if res:
                    scan_results.append(res)
            except Exception:
                pass

    scan_results.sort(key=lambda x: x["port"])
    duration = round(time.time() - start_time, 2)

    return {
        "target": target,
        "ip": ip,
        "hostname": hostname,
        "mode": mode,
        "timestamp": datetime.now().isoformat(),
        "total_scanned": total_ports,
        "open_count": len(scan_results),
        "duration_seconds": duration,
        "open_ports": scan_results
    }


# -------------------------------------------------------------
# Local Port Inspector & Process Terminator
# -------------------------------------------------------------

def inspect_local_ports():
    """Inspect all active listening TCP and UDP sockets on the system"""
    results = []

    # Try ss command first
    cmds = [
        ["ss", "-tulnp"],
        ["netstat", "-tulnp"],
        ["lsof", "-iTCP", "-sTCP:LISTEN", "-n", "-P"]
    ]

    # Prepend sudo if available and not root
    can_sudo = False
    if os.getuid() != 0:
        try:
            import subprocess
            if subprocess.run(["sudo", "-n", "true"], capture_output=True).returncode == 0:
                can_sudo = True
        except Exception:
            pass

    import subprocess
    for cmd in cmds:
        run_cmd = ["sudo"] + cmd if can_sudo else cmd
        try:
            res = subprocess.run(run_cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                lines = res.stdout.strip().splitlines()
                if "ss" in cmd[0]:
                    for line in lines[1:]:
                        parts = re.split(r"\s+", line.strip())
                        if len(parts) >= 5:
                            proto = parts[0].upper()
                            state = parts[1]
                            local = parts[4]
                            proc_info = " ".join(parts[6:]) if len(parts) > 6 else "-"
                            
                            # Extract port
                            port = None
                            if ":" in local:
                                port_str = local.rsplit(":", 1)[1]
                                try:
                                    port = int(port_str)
                                except ValueError:
                                    pass

                            pid = None
                            pname = "-"
                            pid_m = re.search(r"pid=(\d+)", proc_info)
                            if pid_m:
                                pid = int(pid_m.group(1))
                            pname_m = re.search(r'\(\("([^"]+)"', proc_info)
                            if pname_m:
                                pname = pname_m.group(1)

                            if port is not None:
                                db_entry = get_port_info(port, proto.lower())
                                results.append({
                                    "proto": proto,
                                    "local_address": local,
                                    "port": port,
                                    "state": state,
                                    "pid": pid,
                                    "process": pname,
                                    "service": db_entry.get("service", "unknown"),
                                    "name": db_entry.get("name", "")
                                })
                    if results:
                        break
        except Exception:
            continue

    # Fallback to /proc/net/tcp parsing if ss/netstat produced nothing (common in restricted Termux)
    if not results and os.path.exists("/proc/net/tcp"):
        try:
            for path, proto in [("/proc/net/tcp", "TCP"), ("/proc/net/udp", "UDP")]:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        for line in f.readlines()[1:]:
                            fields = line.strip().split()
                            if len(fields) >= 10:
                                state_hex = fields[3]
                                if proto == "TCP" and state_hex != "0A":  # 0A is TCP_LISTEN
                                    continue
                                local_hex = fields[1]
                                ip_hex, port_hex = local_hex.split(":")
                                port = int(port_hex, 16)
                                ip_parts = [str(int(ip_hex[i:i+2], 16)) for i in (6, 4, 2, 0)]
                                ip_str = ".".join(ip_parts)
                                db_entry = get_port_info(port, proto.lower())
                                results.append({
                                    "proto": proto,
                                    "local_address": f"{ip_str}:{port}",
                                    "port": port,
                                    "state": "LISTEN" if proto == "TCP" else "UNCONN",
                                    "pid": None,
                                    "process": "-",
                                    "service": db_entry.get("service", "unknown"),
                                    "name": db_entry.get("name", "")
                                })
        except Exception:
            pass

    # Deduplicate results by (proto, port)
    unique = []
    seen = set()
    for r in results:
        key = (r["proto"], r["port"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    unique.sort(key=lambda x: x["port"])
    return unique


def kill_process_on_port(port, force=False):
    """Find and kill any process occupying the given port"""
    import signal
    import subprocess

    port = int(port)
    pids = set()

    # 1. Try fuser
    try:
        p = subprocess.run(["fuser", f"{port}/tcp"], capture_output=True, text=True)
        for part in p.stdout.strip().split():
            try:
                pids.add(int(part))
            except ValueError:
                pass
    except Exception:
        pass

    # 2. Try lsof
    if not pids:
        try:
            p = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
            for line in p.stdout.strip().splitlines():
                try:
                    pids.add(int(line.strip()))
                except ValueError:
                    pass
        except Exception:
            pass

    # 3. Try parsing ss
    if not pids:
        ports_list = inspect_local_ports()
        for item in ports_list:
            if item["port"] == port and item["pid"]:
                pids.add(item["pid"])

    if not pids:
        return {"success": False, "message": f"No active process found listening on port {port}."}

    killed = []
    for pid in list(pids):
        # Retrieve process name
        pname = "unknown"
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                pname = f.read().replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()
        except Exception:
            try:
                p = subprocess.run(["ps", "-p", str(pid), "-o", "comm="], capture_output=True, text=True)
                pname = p.stdout.strip()
            except Exception:
                pass

        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.4)
            # Check if still running
            try:
                os.kill(pid, 0)
                # Escalate to SIGKILL
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
            killed.append({"pid": pid, "process": pname})
        except PermissionError:
            # Try sudo kill
            try:
                subprocess.run(["sudo", "kill", "-9", str(pid)], check=True)
                killed.append({"pid": pid, "process": pname})
            except Exception as e:
                return {"success": False, "message": f"Permission denied killing PID {pid} ({pname}). Try running with root/sudo."}
        except Exception as e:
            return {"success": False, "message": f"Failed to kill PID {pid}: {e}"}

    return {"success": True, "port": port, "killed": killed}


# -------------------------------------------------------------
# Port Listener & Reverse Shell Catcher
# -------------------------------------------------------------

def start_listener(port, host="0.0.0.0", is_udp=False, output_file=None):
    """Start an interactive socket listener (like Netcat nc -lvnp)"""
    proto_str = "UDP" if is_udp else "TCP"
    print(f"\n{C_CYAN}[*] Starting {proto_str} listener on {host}:{port}...{C_RESET}")
    print(f"{C_GRAY}[*] Press Ctrl+C to stop listening.{C_RESET}\n")

    if is_udp:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))
        try:
            while True:
                data, addr = s.recvfrom(4096)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{C_GREEN}[+] Received datagram from {addr[0]}:{addr[1]} at {timestamp} ({len(data)} bytes):{C_RESET}")
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
                if output_file:
                    with open(output_file, "ab") as f:
                        f.write(data)
        except KeyboardInterrupt:
            print(f"\n{C_YELLOW}[!] UDP Listener terminated.{C_RESET}")
        finally:
            s.close()
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            s.listen(5)
            s.settimeout(1.0)
            print(f"{C_GREEN}[+] Listening for incoming connections on port {port}...{C_RESET}")
            conn = None
            while conn is None:
                try:
                    conn, addr = s.accept()
                except socket.timeout:
                    continue
            conn.settimeout(None)
            print(f"\n{C_GREEN}{C_BOLD}[+] Connection established from {addr[0]}:{addr[1]}!{C_RESET}\n")

            log_f = open(output_file, "ab") if output_file else None

            # Bidirectional streaming
            def receive_loop():
                try:
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            print(f"\n{C_YELLOW}[!] Remote client closed connection.{C_RESET}")
                            break
                        sys.stdout.buffer.write(data)
                        sys.stdout.flush()
                        if log_f:
                            log_f.write(data)
                            log_f.flush()
                except Exception:
                    pass

            t = threading.Thread(target=receive_loop, daemon=True)
            t.start()

            try:
                while t.is_alive():
                    user_input = sys.stdin.readline()
                    if not user_input:
                        break
                    conn.sendall(user_input.encode())
            except KeyboardInterrupt:
                print(f"\n{C_YELLOW}[*] Session closed by user.{C_RESET}")
            finally:
                try:
                    conn.close()
                except:
                    pass
                if log_f:
                    log_f.close()
        except KeyboardInterrupt:
            print(f"\n{C_YELLOW}[*] Listener stopped.{C_RESET}")
        except PermissionError:
            print(f"{C_RED}[!] Error: Binding to port {port} requires root privileges (port < 1024). Run with sudo or use a port >= 1024.{C_RESET}")
        finally:
            s.close()


# -------------------------------------------------------------
# Honeypot & Intrusion Monitor
# -------------------------------------------------------------

def start_honeypot(port, host="0.0.0.0", fake_service="generic"):
    """Start a honeypot listener that logs attacker connections and payloads"""
    log_filename = os.path.join(LOGS_DIR, f"honeypot_port_{port}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    json_filename = log_filename.replace(".log", ".json")

    print(f"\n{C_YELLOW}{C_BOLD}[*] HONEYPOT ACTIVE on {host}:{port} [{fake_service.upper()} EMULATION]{C_RESET}")
    print(f"{C_CYAN}[*] Intrusion logs saving to: {log_filename}{C_RESET}")
    print(f"{C_GRAY}[*] Waiting for incoming scan / intrusion attempts (Press Ctrl+C to stop)...{C_RESET}\n")

    # Service simulation banners
    BANNERS = {
        "ssh": b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n",
        "ftp": b"220 (vsFTPd 3.0.3) Ready for login.\r\n",
        "smtp": b"220 mail.internal.corp ESMTP Postfix (Ubuntu)\r\n",
        "http": b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.52 (Ubuntu)\r\nContent-Type: text/html\r\n\r\n<html><head><title>Corporate Portal</title></head><body><h1>Intranet Login</h1></body></html>",
        "telnet": b"\r\nLinux 5.15.0-generic (kali-corp)\r\nlogin: ",
        "generic": b"Welcome to Service Node 01\r\n"
    }

    banner_data = BANNERS.get(fake_service.lower(), BANNERS["generic"])
    if port == 22:
        banner_data = BANNERS["ssh"]
    elif port == 21:
        banner_data = BANNERS["ftp"]
    elif port in [80, 8080]:
        banner_data = BANNERS["http"]
    elif port == 25:
        banner_data = BANNERS["smtp"]
    elif port == 23:
        banner_data = BANNERS["telnet"]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    all_logs = []

    try:
        s.bind((host, port))
        s.listen(10)
        s.settimeout(1.0)
    except PermissionError:
        print(f"{C_RED}[!] Error: Binding to port {port} requires root privileges (port < 1024). Run with sudo or use a port >= 1024.{C_RESET}")
        return

    try:
        while True:
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{C_RED}{C_BOLD}[!] INTRUSION DETECTED! Connection from {addr[0]}:{addr[1]} at {now_str}{C_RESET}")

            # Send banner
            try:
                conn.sendall(banner_data)
            except Exception:
                pass

            # Read client payload
            payload = b""
            conn.settimeout(3.0)
            try:
                while True:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    payload += chunk
                    if len(payload) > 8192:
                        break
            except Exception:
                pass
            finally:
                try:
                    conn.close()
                except:
                    pass

            text_payload = payload.decode("utf-8", errors="replace")
            hex_payload = payload.hex()

            log_entry = {
                "timestamp": now_str,
                "remote_ip": addr[0],
                "remote_port": addr[1],
                "local_port": port,
                "bytes_received": len(payload),
                "payload_ascii": text_payload,
                "payload_hex": hex_payload
            }
            all_logs.append(log_entry)

            # Write text log
            with open(log_filename, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}] Connection from {addr[0]}:{addr[1]}\n")
                if payload:
                    f.write(f"Payload ({len(payload)} bytes):\n{text_payload}\n")
                    f.write(f"HEX: {hex_payload}\n")
                f.write("-" * 60 + "\n")

            # Write JSON log
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(all_logs, f, indent=2)

            if payload:
                snippet = "".join(c for c in text_payload if c.isprintable())[:100]
                print(f"{C_YELLOW}    Captured Payload ({len(payload)} bytes): {snippet}{C_RESET}\n")

    except KeyboardInterrupt:
        print(f"\n{C_CYAN}[*] Honeypot deactivated. Total intrusions logged: {len(all_logs)}{C_RESET}")
        print(f"{C_GREEN}[+] Log file saved: {log_filename}{C_RESET}")
    finally:
        s.close()


# -------------------------------------------------------------
# Port Forwarder / TCP Proxy
# -------------------------------------------------------------

def start_forwarder(lport, rhost, rport, lhost="0.0.0.0"):
    """Forward incoming connections on local port to a remote host:port"""
    lport, rport = int(lport), int(rport)
    print(f"\n{C_CYAN}{C_BOLD}[*] Starting TCP Forwarder: {lhost}:{lport} -> {rhost}:{rport}{C_RESET}")
    print(f"{C_GRAY}[*] Press Ctrl+C to terminate proxy.{C_RESET}\n")

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        srv.bind((lhost, lport))
        srv.listen(50)
        srv.settimeout(1.0)
    except PermissionError:
        print(f"{C_RED}[!] Error: Binding to local port {lport} requires root privileges.{C_RESET}")
        return

    stats = {"conns": 0, "bytes_fwd": 0, "bytes_rev": 0}

    def pipe(src, dst, is_fwd=True):
        nonlocal stats
        try:
            while True:
                data = src.recv(8192)
                if not data:
                    break
                dst.sendall(data)
                if is_fwd:
                    stats["bytes_fwd"] += len(data)
                else:
                    stats["bytes_rev"] += len(data)
        except Exception:
            pass
        finally:
            try:
                src.close()
            except:
                pass
            try:
                dst.close()
            except:
                pass

    def handle_client(client_sock, client_addr):
        nonlocal stats
        stats["conns"] += 1
        now_str = datetime.now().strftime("%H:%M:%S")
        print(f"{C_GREEN}[+] [{now_str}] New connection from {client_addr[0]}:{client_addr[1]} -> Forwarding to {rhost}:{rport}{C_RESET}")

        try:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.settimeout(5.0)
            remote_sock.connect((rhost, rport))
            remote_sock.settimeout(None)
        except Exception as e:
            print(f"{C_RED}[!] Failed to connect to remote target {rhost}:{rport}: {e}{C_RESET}")
            client_sock.close()
            return

        t1 = threading.Thread(target=pipe, args=(client_sock, remote_sock, True), daemon=True)
        t2 = threading.Thread(target=pipe, args=(remote_sock, client_sock, False), daemon=True)
        t1.start()
        t2.start()

    try:
        while True:
            try:
                c, addr = srv.accept()
            except socket.timeout:
                continue
            th = threading.Thread(target=handle_client, args=(c, addr), daemon=True)
            th.start()
    except KeyboardInterrupt:
        print(f"\n{C_YELLOW}[*] Forwarder stopped.{C_RESET}")
        print(f"{C_CYAN}[*] Summary: Total Clients: {stats['conns']} | Client->Remote: {stats['bytes_fwd']} bytes | Remote->Client: {stats['bytes_rev']} bytes{C_RESET}")
    finally:
        srv.close()


# -------------------------------------------------------------
# Outbound Firewall Egress Tester
# -------------------------------------------------------------

def run_egress_check():
    """Test outbound connectivity on standard ports to test egress firewall restrictions"""
    EGRESS_TARGETS = [
        (21, "FTP", "ftp.gnu.org"),
        (22, "SSH", "github.com"),
        (25, "SMTP", "smtp.gmail.com"),
        (53, "DNS (TCP)", "8.8.8.8"),
        (80, "HTTP", "example.com"),
        (110, "POP3", "pop.gmail.com"),
        (123, "NTP", "pool.ntp.org"),
        (143, "IMAP", "imap.gmail.com"),
        (389, "LDAP", "ldap.forumsys.com"),
        (443, "HTTPS", "cloudflare.com"),
        (465, "SMTPS", "smtp.gmail.com"),
        (587, "Submission", "smtp.gmail.com"),
        (853, "DoT", "1.1.1.1"),
        (993, "IMAPS", "imap.gmail.com"),
        (995, "POP3S", "pop.gmail.com"),
        (1433, "MSSQL", "portquiz.net"),
        (1521, "Oracle", "portquiz.net"),
        (2049, "NFS", "portquiz.net"),
        (3306, "MySQL", "portquiz.net"),
        (3389, "RDP", "portquiz.net"),
        (5432, "Postgres", "portquiz.net"),
        (5900, "VNC", "portquiz.net"),
        (6379, "Redis", "portquiz.net"),
        (8080, "HTTP-Proxy", "portquiz.net"),
        (8443, "HTTPS-Alt", "portquiz.net"),
        (27017, "MongoDB", "portquiz.net")
    ]

    print(f"\n{C_CYAN}{C_BOLD}[*] Testing Outbound Egress Ports (Firewall Egress Inspection)...{C_RESET}")
    print(f"{C_GRAY}[*] Probing 26 standard outbound ports...{C_RESET}\n")

    results = []

    def check_egress(item):
        port, service, test_host = item
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        start = time.time()
        try:
            res = s.connect_ex((test_host, port))
            lat = round((time.time() - start) * 1000, 1)
            s.close()
            status = "ALLOWED" if res == 0 else "BLOCKED/REFUSED"
            return {"port": port, "service": service, "status": status, "host": test_host, "latency": lat}
        except Exception:
            try:
                s.close()
            except:
                pass
            return {"port": port, "service": service, "status": "BLOCKED", "host": test_host, "latency": None}

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
        futures = [ex.submit(check_egress, item) for item in EGRESS_TARGETS]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    results.sort(key=lambda x: x["port"])

    allowed_count = sum(1 for r in results if r["status"] == "ALLOWED")
    blocked_count = len(results) - allowed_count

    print(f"{'PORT':<8} | {'SERVICE':<14} | {'STATUS':<15} | {'TEST HOST':<20} | {'LATENCY'}")
    print("-" * 75)
    for r in results:
        status_color = C_GREEN if r["status"] == "ALLOWED" else C_RED
        lat_str = f"{r['latency']} ms" if r["latency"] is not None else "-"
        print(f"{r['port']:<8} | {r['service']:<14} | {status_color}{r['status']:<15}{C_RESET} | {r['host']:<20} | {lat_str}")

    print("-" * 75)
    print(f"\n{C_BOLD}Egress Summary:{C_RESET} {C_GREEN}{allowed_count} Allowed{C_RESET} | {C_RED}{blocked_count} Filtered/Blocked{C_RESET}")
    if blocked_count > 15:
        print(f"{C_YELLOW}[!] Strict corporate / captive firewall detected. Outbound ports heavily restricted.{C_RESET}")
    else:
        print(f"{C_GREEN}[+] Outbound network allows standard protocol egress.{C_RESET}")
    return results


# -------------------------------------------------------------
# Knowledge Base Lookup
# -------------------------------------------------------------

def lookup_port_db(query):
    """Search knowledge base by port number or service keyword"""
    query_str = str(query).strip().lower()
    matches = []

    # Check if query is integer port
    if query_str.isdigit():
        p = int(query_str)
        if p in PORTS_DB:
            matches.append(PORTS_DB[p])
        else:
            matches.append(get_port_info(p))
    else:
        for p, item in PORTS_DB.items():
            combined = f"{item['service']} {item['name']} {item['desc']} {item['notes']}".lower()
            if query_str in combined:
                matches.append(item)

    return sorted(matches, key=lambda x: x["port"])


# -------------------------------------------------------------
# Report Exporters (TXT, JSON, CSV, Modern Dark HTML)
# -------------------------------------------------------------

def export_json_report(scan_data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scan_data, f, indent=2, ensure_ascii=False)
    return filepath


def export_csv_report(scan_data, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Port", "Protocol", "State", "Service", "Name", "Banner", "Latency (ms)", "Risk", "Security Notes"])
        for p in scan_data.get("open_ports", []):
            writer.writerow([
                p.get("port"),
                p.get("proto"),
                p.get("state"),
                p.get("service"),
                p.get("friendly_name"),
                p.get("banner"),
                p.get("latency_ms"),
                p.get("risk"),
                p.get("notes")
            ])
    return filepath


def export_txt_report(scan_data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("                      PORT SCAN REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Target      : {scan_data.get('target')} ({scan_data.get('ip')})\n")
        f.write(f"Hostname    : {scan_data.get('hostname')}\n")
        f.write(f"Timestamp   : {scan_data.get('timestamp')}\n")
        f.write(f"Mode        : {scan_data.get('mode')}\n")
        f.write(f"Duration    : {scan_data.get('duration_seconds')} seconds\n")
        f.write(f"Total Scanned: {scan_data.get('total_scanned')}\n")
        f.write(f"Open Ports  : {scan_data.get('open_count')}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"{'PORT':<10} | {'SERVICE':<18} | {'RISK':<10} | {'LATENCY':<10} | {'BANNER / DETAILS'}\n")
        f.write("-" * 80 + "\n")
        for p in scan_data.get("open_ports", []):
            port_str = f"{p['port']}/{p['proto']}"
            f.write(f"{port_str:<10} | {p.get('service', ''):<18} | {p.get('risk', ''):<10} | {str(p.get('latency_ms', '')) + 'ms':<10} | {p.get('banner', '')}\n")
            if p.get("notes"):
                f.write(f"  Notes: {p.get('notes')}\n")
        f.write("\n" + "=" * 80 + "\n")
    return filepath


def export_html_report(scan_data, filepath):
    """Generate modern Cyberpunk / SOC dark theme HTML dashboard report"""
    open_ports = scan_data.get("open_ports", [])
    
    # Calculate risk counts
    risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
    for p in open_ports:
        r = p.get("risk", "Low")
        risk_counts[r] = risk_counts.get(r, 0) + 1

    rows_html = []
    for p in open_ports:
        risk = p.get("risk", "Low")
        risk_color = {
            "Critical": "#ff3860",
            "High": "#ff7979",
            "Medium": "#ffdd57",
            "Low": "#48c774",
            "Informational": "#209cee"
        }.get(risk, "#7957d5")

        ssl_badge = ""
        if p.get("ssl"):
            c = p["ssl"]
            ssl_badge = f"""<div class="ssl-box"><strong>TLS Cert:</strong> {c.get('subject')} (Issuer: {c.get('issuer')}, Exp: {c.get('expires')})</div>"""

        banner_text = p.get("banner", "") or "-"
        notes_text = p.get("notes", "") or "-"

        rows_html.append(f"""
        <tr>
            <td><span class="port-badge">{p['port']} / {p['proto']}</span></td>
            <td><strong class="service-title">{p.get('service')}</strong><br><small class="text-muted">{p.get('friendly_name', '')}</small></td>
            <td><span class="tag" style="background:{risk_color}; color:#0a0a0a;">{risk}</span></td>
            <td>{p.get('latency_ms', '-')} ms</td>
            <td>
                <div class="banner-cell">{banner_text}</div>
                {ssl_badge}
            </td>
            <td class="notes-cell">{notes_text}</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Port Scan Report - {scan_data.get('target')}</title>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: #151d2f;
            --accent: #00ffcc;
            --text-color: #e2e8f0;
            --border: #233044;
        }}
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 24px;
        }}
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .logo {{
            font-size: 26px;
            font-weight: 800;
            color: var(--accent);
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .logo span {{
            color: #ff3860;
        }}
        .badge-edition {{
            background: #1e293b;
            color: #38bdf8;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 13px;
            margin-left: 10px;
            border: 1px solid #334155;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .card-label {{
            font-size: 12px;
            text-transform: uppercase;
            color: #94a3b8;
            letter-spacing: 0.5px;
        }}
        .card-value {{
            font-size: 26px;
            font-weight: 700;
            color: #fff;
            margin-top: 6px;
        }}
        .search-box {{
            width: 100%;
            padding: 12px 16px;
            background: #151d2f;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #fff;
            font-size: 15px;
            margin-bottom: 16px;
            box-sizing: border-box;
        }}
        .search-box:focus {{
            outline: none;
            border-color: var(--accent);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
        }}
        th, td {{
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #1a233a;
            color: #94a3b8;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        tr:hover td {{
            background: rgba(255,255,255,0.02);
        }}
        .port-badge {{
            font-family: monospace;
            background: #0f172a;
            border: 1px solid #334155;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            color: var(--accent);
        }}
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .ssl-box {{
            margin-top: 6px;
            padding: 6px 8px;
            background: #0d1525;
            border-left: 3px solid #38bdf8;
            border-radius: 4px;
            font-size: 12px;
            color: #93c5fd;
        }}
        .banner-cell {{
            font-family: monospace;
            font-size: 13px;
            color: #cbd5e1;
            word-break: break-word;
        }}
        .notes-cell {{
            font-size: 13px;
            color: #94a3b8;
            max-width: 320px;
            word-wrap: break-word;
        }}
        .text-muted {{ color: #64748b; font-size: 12px; }}
        .footer {{
            margin-top: 32px;
            text-align: center;
            color: #64748b;
            font-size: 13px;
            border-top: 1px solid var(--border);
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="logo">PORT<span>X</span> <span class="badge-edition">Kali Linux & Termux Edition</span></div>
                <div style="margin-top:6px; color:#94a3b8; font-size:14px;">Advanced Network Port & Security Audit Report</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:14px; color:#94a3b8;">Generated: <strong>{scan_data.get('timestamp')}</strong></div>
                <div style="font-size:14px; color:var(--accent);">Target: <strong>{scan_data.get('target')} ({scan_data.get('ip')})</strong></div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-label">Total Ports Scanned</div>
                <div class="card-value">{scan_data.get('total_scanned')}</div>
            </div>
            <div class="card">
                <div class="card-label">Open Ports Found</div>
                <div class="card-value" style="color:var(--accent);">{scan_data.get('open_count')}</div>
            </div>
            <div class="card">
                <div class="card-label">Scan Duration</div>
                <div class="card-value">{scan_data.get('duration_seconds')}s</div>
            </div>
            <div class="card">
                <div class="card-label">Critical / High Risks</div>
                <div class="card-value" style="color:#ff3860;">{risk_counts['Critical'] + risk_counts['High']}</div>
            </div>
        </div>

        <input type="text" id="searchInput" class="search-box" placeholder="Search open ports, services, banners, or notes...">

        <table>
            <thead>
                <tr>
                    <th>Port / Proto</th>
                    <th>Service / Name</th>
                    <th>Risk Rating</th>
                    <th>RTT Latency</th>
                    <th>Banner / Service Signature</th>
                    <th>Security Assessment & Notes</th>
                </tr>
            </thead>
            <tbody id="portsTable">
                {"".join(rows_html) if rows_html else '<tr><td colspan="6" style="text-align:center; padding:30px; color:#64748b;">No open ports identified.</td></tr>'}
            </tbody>
        </table>

        <div class="footer">
            Generated with Port Tool (Advanced Internet Port Suite for Kali Linux & Termux) &bull; For Authorized Security Testing Only
        </div>
    </div>

    <script>
        document.getElementById('searchInput').addEventListener('keyup', function() {{
            const val = this.value.toLowerCase();
            const rows = document.querySelectorAll('#portsTable tr');
            rows.forEach(r => {{
                r.style.display = r.innerText.toLowerCase().includes(val) ? '' : 'none';
            }});
        }});
    </script>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filepath


# -------------------------------------------------------------
# CLI Entrypoint for Engine
# -------------------------------------------------------------

import signal
def _sig_handler(signum, frame):
    raise KeyboardInterrupt
signal.signal(signal.SIGTERM, _sig_handler)

def main():
    parser = argparse.ArgumentParser(description="Port - Advanced Networking Engine for Kali & Termux")
    subparsers = parser.add_subparsers(dest="action")

    # SCAN subcommand
    p_scan = subparsers.add_parser("scan", help="Scan remote target ports")
    p_scan.add_argument("-t", "--target", required=True, help="Target host or IP")
    p_scan.add_argument("-p", "--ports", default="top100", help="Ports (e.g. 'top20', 'top100', '1-1000', '80,443')")
    p_scan.add_argument("-m", "--mode", choices=["fast", "deep", "udp"], default="fast", help="Scan mode")
    p_scan.add_argument("-T", "--threads", type=int, default=100, help="Concurrency worker threads")
    p_scan.add_argument("-W", "--timeout", type=float, default=1.5, help="Socket timeout in seconds")
    p_scan.add_argument("-o", "--output", help="Save report to file (.txt, .json, .csv, .html)")
    p_scan.add_argument("--json", action="store_true", help="Print raw JSON to stdout")

    # INSPECT subcommand
    p_inspect = subparsers.add_parser("inspect", help="Inspect local active listening ports")
    p_inspect.add_argument("--json", action="store_true", help="Output JSON")

    # KILL subcommand
    p_kill = subparsers.add_parser("kill", help="Kill process occupying a local port")
    p_kill.add_argument("-p", "--port", type=int, required=True, help="Port number")
    p_kill.add_argument("-f", "--force", action="store_true", help="Kill immediately without prompt")

    # LISTEN subcommand
    p_listen = subparsers.add_parser("listen", help="Start port listener / reverse shell receiver")
    p_listen.add_argument("-p", "--port", type=int, required=True, help="Port to listen on")
    p_listen.add_argument("-b", "--bind", default="0.0.0.0", help="Bind IP address")
    p_listen.add_argument("-u", "--udp", action="store_true", help="UDP listener")
    p_listen.add_argument("-o", "--output", help="Save stream to file")

    # HONEYPOT subcommand
    p_pot = subparsers.add_parser("honeypot", help="Start intrusion honeypot on port")
    p_pot.add_argument("-p", "--port", type=int, required=True, help="Port number")
    p_pot.add_argument("-b", "--bind", default="0.0.0.0", help="Bind IP address")
    p_pot.add_argument("-s", "--service", default="generic", help="Service emulation (ssh, ftp, http, smtp, telnet)")

    # FORWARD subcommand
    p_fwd = subparsers.add_parser("forward", help="TCP port forwarder / proxy")
    p_fwd.add_argument("-l", "--lport", type=int, required=True, help="Local listen port")
    p_fwd.add_argument("-r", "--remote", required=True, help="Remote host:port (e.g. 192.168.1.100:80)")
    p_fwd.add_argument("-b", "--bind", default="0.0.0.0", help="Local bind address")

    # EGRESS subcommand
    p_egress = subparsers.add_parser("egress", help="Test outbound firewall egress ports")

    # LOOKUP subcommand
    p_lookup = subparsers.add_parser("lookup", help="Lookup port knowledgebase")
    p_lookup.add_argument("query", help="Port number or service keyword")

    args = parser.parse_args()

    if args.action == "scan":
        ports = parse_ports(args.ports)
        
        def on_prog(done, total):
            if not args.json and sys.stdout.isatty():
                pct = int((done / total) * 100)
                sys.stdout.write(f"\r{C_CYAN}[*] Scanning {args.target} ({pct}% - {done}/{total} ports)...{C_RESET}")
                sys.stdout.flush()

        data = run_port_scan(args.target, ports, mode=args.mode, threads=args.threads, timeout=args.timeout, progress_cb=on_prog)
        if not args.json and sys.stdout.isatty():
            sys.stdout.write("\r" + " " * 60 + "\r")
            sys.stdout.flush()

        if "error" in data:
            print(f"{C_RED}[!] Error: {data['error']}{C_RESET}")
            sys.exit(1)

        if args.json:
            print(json.dumps(data, indent=2))
        else:
            # Print beautiful console summary table
            print(f"\n{C_BOLD}Scan Results for {C_GREEN}{data['target']}{C_RESET} ({data['ip']}){C_RESET}")
            print(f"Total Scanned: {data['total_scanned']} | Open: {C_GREEN}{data['open_count']}{C_RESET} | Duration: {data['duration_seconds']}s\n")

            if data["open_ports"]:
                print(f"{'PORT':<10} | {'SERVICE':<16} | {'RISK':<10} | {'RTT':<8} | {'BANNER / DETAILS'}")
                print("-" * 85)
                for p in data["open_ports"]:
                    port_str = f"{p['port']}/{p['proto']}"
                    risk = p.get("risk", "Low")
                    risk_color = {
                        "Critical": C_RED + C_BOLD,
                        "High": C_RED,
                        "Medium": C_YELLOW,
                        "Low": C_GREEN,
                        "Informational": C_CYAN
                    }.get(risk, C_WHITE)

                    banner_display = p.get("banner", "")
                    if p.get("ssl"):
                        c = p["ssl"]
                        banner_display += f" [TLS: {c.get('subject')}]"

                    print(f"{port_str:<10} | {p.get('service', 'unknown'):<16} | {risk_color}{risk:<10}{C_RESET} | {str(p.get('latency_ms', '')) + 'ms':<8} | {banner_display[:35]}")
                print("-" * 85)
            else:
                print(f"{C_YELLOW}[!] No open ports detected on target within specified range.{C_RESET}")

        # Handle export
        if args.output:
            out_path = args.output
            if out_path.endswith(".json"):
                export_json_report(data, out_path)
            elif out_path.endswith(".csv"):
                export_csv_report(data, out_path)
            elif out_path.endswith(".html"):
                export_html_report(data, out_path)
            else:
                export_txt_report(data, out_path)
            print(f"\n{C_GREEN}[+] Report exported to: {out_path}{C_RESET}")

    elif args.action == "inspect":
        ports = inspect_local_ports()
        if args.json:
            print(json.dumps(ports, indent=2))
        else:
            print(f"\n{C_BOLD}Active Local Listening Ports:{C_RESET}\n")
            print(f"{'PROTO':<6} | {'LOCAL ADDRESS':<22} | {'PORT':<7} | {'PID':<8} | {'PROCESS':<18} | {'SERVICE'}")
            print("-" * 80)
            for item in ports:
                pid_str = str(item['pid']) if item['pid'] else "-"
                print(f"{item['proto']:<6} | {item['local_address']:<22} | {item['port']:<7} | {pid_str:<8} | {item['process']:<18} | {item['service']}")
            print("-" * 80)
            print(f"Total Listening Ports: {len(ports)}\n")

    elif args.action == "kill":
        res = kill_process_on_port(args.port, force=args.force)
        if res["success"]:
            print(f"{C_GREEN}[+] Successfully freed port {args.port}. Terminated processes:{C_RESET}")
            for k in res["killed"]:
                print(f"    - PID {k['pid']} ({k['process']})")
        else:
            print(f"{C_RED}[!] {res['message']}{C_RESET}")

    elif args.action == "listen":
        start_listener(args.port, host=args.bind, is_udp=args.udp, output_file=args.output)

    elif args.action == "honeypot":
        start_honeypot(args.port, host=args.bind, fake_service=args.service)

    elif args.action == "forward":
        if ":" not in args.remote:
            print(f"{C_RED}[!] Error: Remote target must be in format HOST:PORT (e.g. 192.168.1.100:80){C_RESET}")
            sys.exit(1)
        rhost, rport = args.remote.split(":", 1)
        start_forwarder(args.lport, rhost, rport, lhost=args.bind)

    elif args.action == "egress":
        run_egress_check()

    elif args.action == "lookup":
        results = lookup_port_db(args.query)
        if not results:
            print(f"{C_YELLOW}[!] No matching ports found for query: {args.query}{C_RESET}")
        else:
            print(f"\n{C_BOLD}Knowledge Base Results for '{args.query}':{C_RESET}\n")
            for item in results:
                risk = item.get("risk", "Low")
                risk_color = {
                    "Critical": C_RED + C_BOLD,
                    "High": C_RED,
                    "Medium": C_YELLOW,
                    "Low": C_GREEN,
                    "Informational": C_CYAN
                }.get(risk, C_WHITE)

                print(f"{C_CYAN}Port {item['port']} / {item['proto'].upper()}{C_RESET} - {C_BOLD}{item['name']}{C_RESET} ({item['service']})")
                print(f"  Description : {item.get('desc', '')}")
                print(f"  Risk Level  : {risk_color}{risk}{C_RESET}")
                if item.get("notes"):
                    print(f"  Security    : {item['notes']}")
                print("-" * 65)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
