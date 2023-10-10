import config

if not config.IS_DEBUG:
    from INA260_bridge import get_voltage

max_readings = 200
min_charge_slope = 0.1 / 10000
skip_updates = 4


class ChargeController:
    latest_voltage_readings = []
    updates_since_last_read = 0
    charging = False
    slope = 0

    def update(self):
        if self.updates_since_last_read < skip_updates:
            self.updates_since_last_read += 1
            return
        else:
            self.updates_since_last_read = 0

        if len(self.latest_voltage_readings) >= max_readings:
            self.latest_voltage_readings.pop(0)

        self.latest_voltage_readings.append(get_voltage())
        self.slope = self.calc_charge_slope()

    def get_charge_slope(self):
        return self.slope

    def calc_charge_slope(self):

        if len(self.latest_voltage_readings) == 0:
            return 0

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
        denomerator = sum([pow(deviation_x, 2) for deviation_x in deviation_xs])

        if denomerator == 0:
            return 1

        return numerator / denomerator

    def is_charging(self):
        return self.slope > min_charge_slope
