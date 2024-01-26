import os
import sys

IS_DEBUG = os.environ.get("DEBUG") or (len(sys.argv) >= 2 and sys.argv[1] == "nopi")

# General
IDLE_TIMEOUT_S = 60 * 5
RELOAD_CHARGE_VOLTAGE = 8.2
FOLLOW_QR_DIRECTLY = False
