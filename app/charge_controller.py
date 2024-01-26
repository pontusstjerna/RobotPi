import RPi.GPIO as io

# Set mode to GPIO numbers (not PIN numbers)
io.setmode(io.BCM)


charge_read_pin = 6
relay_switch_pin = 26

io.setup(relay_switch_pin, io.OUT)
io.setup(charge_read_pin, io.IN)

io.output(relay_switch_pin, False)

def enable_charge():
    io.output(relay_switch_pin, io.HIGH)

def disable_charge():
    io.output(relay_switch_pin, io.LOW)

def is_charging_connected():
    return io.input(charge_read_pin) == 1

def is_charging_enabled():
    return io.input(relay_switch_pin) == 1

def exit():
    io.cleanup()
