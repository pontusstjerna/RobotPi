import RPi.GPIO as io

# Set mode to GPIO numbers (not PIN numbers) 
io.setmode(io.BCM)


pin_number = 16

io.setup(pin_number, io.OUT)

io.output(pin_number, False)

def setState(state):
    if state == "close":
        io.output(pin_number, False)
    elif state == "open":
        io.output(pin_number, True)

def getState():
    value = io.input(pin_number) 
    return "open" if value else "close"

def exit():
    io.cleanup()
