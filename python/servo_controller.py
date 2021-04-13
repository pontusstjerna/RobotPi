import RPi.GPIO as io
import time

pin_number = 14
max_cycle = 12.5
min_cycle = 2.5
frequency = 50
sleep_s = 0.2
servo_speed = 0.1

# Set mode to GPIO numbers (not PIN numbers) 
io.setmode(io.BCM)
io.setup(pin_number, io.OUT)

# 50Hz for servo
pwm = io.PWM(pin_number, frequency)

current_speed = 0.0
current_cycle = max_cycle - (max_cycle - min_cycle) * 0.5

pwm.start(0)

while current_speed != 0:
  current_cycle = max(min_cycle, min(max_cycle, current_cycle + current_speed))
  pwm.ChangeDutyCycle(current_cycle)
  time.sleep(sleep_s)
  if current_cycle == min_cycle or current_cycle == max_cycle:
    stop()

def increase_angle():
  current_speed = servo_speed

def decrease_angle():
  current_speed = -servo_speed

def stop():
  speed = 0
  pwm.ChangeDutyCycle(0)

def exit():
  pwm.stop()
  io.cleanup()
