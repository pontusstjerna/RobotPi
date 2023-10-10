import os
import sys

IS_DEBUG = os.environ.get("DEBUG") or (len(sys.argv) >= 2 and sys.argv[1] == "nopi")

# General
REDOCK_INTERVAL = int(os.environ.get("REDOCK_INTERVAL_S") or 3600)
IDLE_TIMEOUT_S = 60 * 5
MAX_REDOCK_ATTEMPTS = 5
REDOCK_VOLTAGE = 7.65
