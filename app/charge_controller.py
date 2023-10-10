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
        xs = range(len(self.latest_voltage_readings))
        ys = self.latest_voltage_readings

        avg_xs = sum(xs) / len(xs)
        avg_ys = sum(ys) / len(ys)

        deviation_xs = [x - avg_xs for x in xs]
        deviation_ys = [y - avg_ys for y in ys]

        numerator = sum(
            [deviation_xs[i] * deviation_ys[i] for i in range(len(deviation_xs))]
        )
        denomerator = sum([pow(deviation_x) for deviation_x in deviation_xs])

        return numerator / denomerator

    def is_charging(self):
        slope = self.calc_charge_slope()
        if slope <= 0:  # We are losing current over time
            return False
        else:  # We are gaining current over time
            return True
