import RPi.GPIO as io

io.setmode(io.BCM)
PWM_MAX = 100

# A:
#  INT1 = 14 = rear right backward
#  INT2 = 15 = rear right forward
#  INT3 = 18 = front right backward
#  INT4 = 23 = front right forward

# B:
#  INT1 = 17 = front left forward
#  INT2 = 27 = front left backward
#  INT3 = 22 = rear left forward
#  INT4 = 10 = rear left backward


class Motor:

    forward_pwm: io.PWM
    reverse_pwm: io.PWM

    def __init__(self, forward_pin: int, reverse_pin: int):
        io.setup(forward_pin, io.OUT)
        io.setup(reverse_pin, io.OUT)

        self.forward_pwm = io.PWM(forward_pin, PWM_MAX)
        self.reverse_pwm = io.PWM(reverse_pin, PWM_MAX)

        self.forward_pwm.start(0)
        self.reverse_pwm.start(0)

        self.forward_pwm.ChangeDutyCycle(0)
        self.reverse_pwm.ChangeDutyCycle(0)

    def run(self, percent: int):
        if percent > 0:
            self.forward_pwm.ChangeDutyCycle(min(percent, PWM_MAX))
        elif percent < 0:
            self.reverse_pwm.ChangeDutyCycle(min(-percent, PWM_MAX))

        else:
            self.stop()

    def stop(self):
        self.forward_pwm.ChangeDutyCycle(0)
        self.reverse_pwm.ChangeDutyCycle(0)


rear_right = Motor(15, 14)
front_right = Motor(23, 18)
front_left = Motor(17, 27)
rear_left = Motor(22, 10)


def set_right_motors(percent: int):
    rear_right.run(percent)
    front_right.run(percent)


def set_left_motors(percent: int):
    rear_left.run(percent)
    front_left.run(percent)


def cleanup():
    set_right_motors(0)
    set_left_motors(0)
    io.cleanup()
