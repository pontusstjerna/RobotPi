import sys
import time
import L298NHBridge as HBridge
import IRF520Bridge as MOSFETBridge
import servo_controller

print('Python controller ready.')
sys.stdout.flush()

inp = ""

while inp != 'quit':
    inp = sys.stdin.readline().split('\n')[0]
    if inp == 'getMOSFET':
        print("MOSFET: " + MOSFETBridge.getState())
        sys.stdout.flush()
    elif inp != 'quit':
        print (inp)
        sys.stdout.flush()

        try:
            eval(inp)
        except Exception as err:
            print('Unable to execute')
            print (err)
            pass

print('User quit')
HBridge.exit()
MOSFETBridge.exit()
servo_controller.exit()
