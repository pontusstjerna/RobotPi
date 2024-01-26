import subprocess
import config

if not config.IS_DEBUG:
    from INA260_bridge import get_voltage, get_current


def get_status(controller):

    if config.IS_DEBUG:
        return {}

    # Example result: b"throttled=0x0\ntemp=44.0'C\nvolt=1.2875V\nvolt=1.2000V\nvolt=1.2000V\nvolt=1.2250V\n"
    # status_string = subprocess.check_output(["sh", "get_status.sh"])
    voltage = get_voltage()

    return {
        "power": controller.power,
        "temp": "Super hot",
        "voltage": voltage,
        "current": get_current(),
        "volts": {
            "core": voltage
        }
    }
