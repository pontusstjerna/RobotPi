import config

if not config.IS_DEBUG:
    from INA260_bridge import get_current


def is_charging_connected():
    return get_current() < 200
