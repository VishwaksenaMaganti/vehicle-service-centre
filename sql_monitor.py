"""
========================================================================
AUTOCARE PRECISION - REAL-TIME SQL QUERY MONITOR (MySQL 8.0)
========================================================================
This script continuously tails and displays SQL queries executed by the
Vehicle Service Centre web application in real time in a separate shell.
"""

import os
import sys
import time
import re

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql_execution.log")

# ANSI Color codes for Windows 10/11 Command Prompt & PowerShell
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Enable VT100 escape sequence processing in Windows cmd.exe
if os.name == 'nt':
    os.system('')
    os.system('title MySQL 8.0 Real-Time SQL Query Stream - AutoCare Precision')


def print_banner():
    print(f"{CYAN}{BOLD}+============================================================================+{RESET}")
    print(f"{CYAN}{BOLD}|        AUTOCARE PRECISION - REAL-TIME SQL QUERY MONITOR (MySQL 8.0)        |{RESET}")
    print(f"{CYAN}{BOLD}+============================================================================+{RESET}")
    print(f"{WHITE} Database Target :{RESET} {GREEN}{BOLD}vehicle_service_centre{RESET}")
    print(f"{WHITE} Engine & Port   :{RESET} MySQL 8.0 Community Server @ localhost:3306")
    print(f"{WHITE} Monitoring File :{RESET} {LOG_FILE}")
    print(f"{WHITE} Live Status     :{RESET} {GREEN}ACTIVE LISTENING (Interact with the Web App to see queries){RESET}")
    print(f"{GRAY} Press Ctrl + C to exit the monitor at any time.{RESET}")
    print(f"{CYAN}+----------------------------------------------------------------------------+{RESET}\n")


def format_sql_log_line(line):
    line = line.strip()
    if not line:
        return

    # Pattern: [timestamp] [TYPE] query | PARAMS: params | status
    pattern = r"^\[(.*?)\]\s*\[(.*?)\]\s*(.*?)\s*\|\s*PARAMS:\s*(.*?)\s*\|\s*(.*?)$"
    match = re.match(pattern, line)

    if match:
        timestamp, q_type, query, params, status = match.groups()
        is_write = q_type.upper() == "WRITE"
        is_error = "ERROR" in status.upper()

        if is_error:
            box_color = RED
            badge = f"{RED}{BOLD}[SQL ERROR / ROLLBACK]{RESET}"
        elif is_write:
            box_color = GREEN
            badge = f"{GREEN}{BOLD}[TRANSACTION WRITE (COMMIT)]{RESET}"
        else:
            box_color = CYAN
            badge = f"{CYAN}{BOLD}[SQL READ QUERY]{RESET}"

        print(f"{box_color}+-- {badge} {WHITE}{timestamp}{RESET} {box_color}--------------------------------{RESET}")
        print(f"{box_color}|{RESET} {BOLD}SQL     :{RESET} {WHITE}{query}{RESET}")
        if params and params != "None" and params != "()":
            print(f"{box_color}|{RESET} {GRAY}PARAMS  :{RESET} {YELLOW}{params}{RESET}")
        print(f"{box_color}|{RESET} {GRAY}STATUS  :{RESET} {GREEN if not is_error else RED}{status}{RESET}")
        print(f"{box_color}+----------------------------------------------------------------------------+{RESET}\n")
    else:
        # Fallback raw line
        print(f"{GRAY}[RAW SQL LOG]{RESET} {line}")


def tail_log():
    print_banner()

    # Ensure log file exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("")

    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        # Print the last few lines if any
        lines = f.readlines()
        if lines:
            print(f"{GRAY}--- Displaying recent query history ({len(lines[-10:])} queries) ---{RESET}\n")
            for line in lines[-10:]:
                format_sql_log_line(line)
            print(f"{GREEN}--- Now streaming real-time queries ---{RESET}\n")

        # Seek to the end of the file for live tailing
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if line:
                format_sql_log_line(line)
            else:
                time.sleep(0.1)


if __name__ == "__main__":
    try:
        tail_log()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[*] SQL Monitor stopped by user.{RESET}")
        sys.exit(0)
