import RPi.GPIO as io
import time
import threading

pin_number = 14
max_cycle = 12
min_cycle = 3
frequency = 50
sleep_s = 0.02
servo_speed = 0.05

# Set mode to GPIO numbers (not PIN numbers) 
io.setwarnings(False)
io.setmode(io.BCM)
io.setup(pin_number, io.OUT)

# 50Hz for servo
pwm = io.PWM(pin_number, frequency)

current_speed = 0.0
current_cycle = 7.5

pwm.start(0)

def exec_servo():
  global current_cycle
  current_cycle = max(min_cycle, min(max_cycle, current_cycle + current_speed))
  pwm.ChangeDutyCycle(current_cycle)

  if current_cycle == min_cycle or current_cycle == max_cycle:
    stop()

  # Run this function again after sleep_s seconds
  if current_speed != 0:
    threading.Timer(sleep_s, exec_servo).start()

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
  # pwm.ChangeDutyCycle(0)

def exit():
  pwm.stop()
  io.cleanup()
