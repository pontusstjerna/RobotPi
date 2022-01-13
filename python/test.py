import sys
import time

print("Python started (TEST VERSION)")
sys.stdout.flush()

inp = ""

while inp != "quit":
    inp = sys.stdin.readline()
    inp = inp.split("\n")[0]
    print(inp)
    sys.stdout.flush()
