from datetime import datetime
import time
import config

if not config.IS_DEBUG:
    from INA260_bridge import get_voltage
    import relay_bridge as relay


class Timer:
    start_time = datetime.now()

    def __init__(self, interval, action):
        self.interval = interval
        self.action = action

    def update(self):
        if self.start_time + self.interval <= datetime.now():
            self.start_time = datetime.now()
            self.action()


def reload_charge():
    voltage = get_voltage()
    if voltage < config.RELOAD_CHARGE_VOLTAGE:
        if voltage < 5:
            print(
                f"Voltage unreasonably low ({round(voltage, 2)}v) - will not reload charging"
            )
        else:
            print(
                f"Voltage below {config.RELOAD_CHARGE_VOLTAGE}v ({round(voltage, 2)}v), will reload charging"
            )
            relay.set_state("close")
            time.sleep(5)
            relay.set_state("open")
