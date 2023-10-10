import config

if not config.IS_DEBUG:
    from INA260_bridge import get_voltage

max_readings = 50


class ChargeController:
    latest_voltage_readings = []
    charging = False

    def update(self):
        if len(self.latest_voltage_readings) >= max_readings:
            self.latest_voltage_readings.pop(0)

        self.latest_voltage_readings.append(get_voltage())

    def calc_charge_slope(self):
        # using a formula to calculate approx. slope, see: https://www.varsitytutors.com/hotmath/hotmath_help/topics/line-of-best-fit
        return 0

    def is_charging(self):
        slope = self.calc_charge_slope()
        if slope < 0: # We are losing current over time
            return False
        else: # We are gaining current over time
            return True
