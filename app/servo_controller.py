import RPi.GPIO as io
import pigpio
import time
import threading

pin_number = 14
max_cycle = 2000
min_cycle = 660
sleep_s = 0.02
servo_speed = 5

# Set mode to GPIO numbers (not PIN numbers)
io.setwarnings(False)
io.setmode(io.BCM)
io.setup(pin_number, io.OUT)

current_speed = 0.0
current_cycle = 1500

pi = pigpio.pi()


def exec_servo():
    # Run this function again after sleep_s seconds if we haven't stopped
    if current_speed != 0:
        threading.Timer(sleep_s, exec_servo).start()
    else:
        return

    global current_cycle
    current_cycle = max(min_cycle, min(max_cycle, current_cycle + current_speed))
    pi.set_servo_pulsewidth(pin_number, current_cycle)

    if current_cycle == min_cycle or current_cycle == max_cycle:
        stop()


def increase_angle():
    global current_speed
    current_speed = servo_speed
    exec_servo()


def decrease_angle():
    global current_speed
    current_speed = -servo_speed
    exec_servo()


def stop():
    global current_speed
    current_speed = 0
    pi.set_servo_pulsewidth(pin_number, 0)


def exit():
    pi.stop()
    io.cleanup()
