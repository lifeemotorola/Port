#!/usr/bin/env bash
# ==============================================================================
# Comprehensive Test Suite for Port Tool
# Tests all modules, flags, scanners, and reporters
# ==============================================================================

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT_CMD="$SCRIPT_DIR/port.sh"
TEST_LOGS="$SCRIPT_DIR/tests/test_output"
mkdir -p "$TEST_LOGS"

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
CYAN="\033[0;36m"
BOLD="\033[1m"
RESET="\033[0m"

PASSED=0
FAILED=0

run_test() {
    local test_name="$1"
    local command="$2"

    echo -ne "  ${CYAN}[TEST]${RESET} ${test_name}... "
    if eval "$command" > "$TEST_LOGS/last_test.log" 2>&1; then
        echo -e "${GREEN}${BOLD}PASSED${RESET}"
        ((PASSED++))
    else
        echo -e "${RED}${BOLD}FAILED${RESET}"
        echo -e "  ${RED}Error log output:${RESET}"
        cat "$TEST_LOGS/last_test.log" | tail -n 15
        ((FAILED++))
    fi
}

echo -e "\n${BOLD}======================================================${RESET}"
echo -e "      PORT TOOL AUTOMATED INTEGRATION TEST SUITE      "
echo -e "${BOLD}======================================================${RESET}\n"

# Test 1: Executable permissions
run_test "Script is executable" "[ -x '$PORT_CMD' ]"

# Test 2: Help flag
run_test "Help argument (-h / --help)" "'$PORT_CMD' --help | grep -q 'USAGE:'"

# Test 3: Version argument
run_test "Version argument (-v / --version)" "'$PORT_CMD' -v | grep -q 'Port Tool v2.1.0'"

# Test 4: Local port inspection
run_test "Local port inspector (-i / --inspect)" "'$PORT_CMD' -i | grep -q 'Active Local Listening Ports:'"

# Test 5: Knowledge base port lookup by number
run_test "Knowledge base lookup by port (445)" "'$PORT_CMD' -q 445 | grep -q 'SMB over TCP/IP'"

# Test 6: Knowledge base lookup by keyword
run_test "Knowledge base lookup by keyword (redis)" "'$PORT_CMD' -q redis | grep -q 'Redis In-Memory Database'"

# Test 7: Fast TCP scan on localhost
run_test "Fast TCP scan on localhost (port 22)" "'$PORT_CMD' -t 127.0.0.1 -p 22 -m fast | grep -q '22/tcp'"

# Test 8: Deep banner grab on localhost SSH
run_test "Deep banner grabbing (port 22)" "'$PORT_CMD' -t 127.0.0.1 -p 22 -m deep | grep -iq 'SSH-'"

# Test 9: HTML report export
HTML_REP="$SCRIPT_DIR/reports/test_automated_report.html"
run_test "HTML report export" "'$PORT_CMD' -t 127.0.0.1 -p 22,111 -o '$HTML_REP' && [ -s '$HTML_REP' ] && grep -q 'PORT.*X' '$HTML_REP'"

# Test 10: JSON report export
JSON_REP="$SCRIPT_DIR/reports/test_automated_report.json"
run_test "JSON report export" "'$PORT_CMD' -t 127.0.0.1 -p 22 -o '$JSON_REP' && [ -s '$JSON_REP' ] && grep -q '\"open_ports\"' '$JSON_REP'"

# Test 11: CSV report export
CSV_REP="$SCRIPT_DIR/reports/test_automated_report.csv"
run_test "CSV report export" "'$PORT_CMD' -t 127.0.0.1 -p 22 -o '$CSV_REP' && [ -s '$CSV_REP' ] && grep -q '22,tcp' '$CSV_REP'"

# Test 12: Kill process on port
run_test "Kill process on port (-k / --kill)" "
    python3 -c 'import socket, time; s = socket.socket(); s.bind((\"127.0.0.1\", 37777)); s.listen(1); time.sleep(10)' &
    DUMMY_PID=\$!
    sleep 0.5
    '$PORT_CMD' -k 37777 --force | grep -q 'Successfully freed port 37777'
    ! kill -0 \$DUMMY_PID 2>/dev/null
"

# Test 13: TCP Forwarder
run_test "TCP Port Forwarder (-f / --forward)" "
    '$PORT_CMD' -f 37776:127.0.0.1:22 &
    FWD_PID=\$!
    sleep 0.5
    RESP=\$(python3 -c 'import socket; s = socket.socket(); s.settimeout(2.0); s.connect((\"127.0.0.1\", 37776)); print(s.recv(1024).decode()); s.close()')
    kill -15 \$FWD_PID 2>/dev/null || true
    echo \"\$RESP\" | grep -q 'SSH-'
"

# Test 14: Honeypot intrusion detection and payload logging
run_test "Honeypot intrusion detection (--honeypot)" "
    '$PORT_CMD' --honeypot 37775 --service ssh &
    POT_PID=\$!
    sleep 0.5
    python3 -c 'import socket; s = socket.socket(); s.settimeout(2.0); s.connect((\"127.0.0.1\", 37775)); s.recv(1024); s.sendall(b\"TEST_PAYLOAD_AUTOTEST\"); s.close()'
    sleep 0.5
    kill -15 \$POT_PID 2>/dev/null || true
    cat '$SCRIPT_DIR'/logs/honeypot_port_37775_*.log | grep -q 'TEST_PAYLOAD_AUTOTEST'
"

# Clean up test reports
rm -f "$HTML_REP" "$JSON_REP" "$CSV_REP" "$SCRIPT_DIR"/logs/honeypot_port_37775_*.log "$SCRIPT_DIR"/logs/honeypot_port_37775_*.json

echo -e "\n${BOLD}======================================================${RESET}"
echo -e "  TOTAL TESTS : $((PASSED + FAILED))"
echo -e "  ${GREEN}PASSED      : ${PASSED}${RESET}"
if [ "$FAILED" -gt 0 ]; then
    echo -e "  ${RED}FAILED      : ${FAILED}${RESET}"
    exit 1
else
    echo -e "  ${GREEN}${BOLD}ALL TESTS PASSED SUCCESSFULLY!${RESET}"
fi
echo -e "${BOLD}======================================================${RESET}\n"
