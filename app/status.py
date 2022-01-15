import subprocess


def get_status(controller):
    # Example result: b"throttled=0x0\ntemp=44.0'C\nvolt=1.2875V\nvolt=1.2000V\nvolt=1.2000V\nvolt=1.2250V\n"
    status_string = subprocess.check_output(["sh", "get_status.sh"])
    split = status_string.decode("utf-8").split("\n")
    status_values = [*map(get_status_value, split)]

    return {
        "power": controller.power,
        "throttled": get_throttled_bit_status(status_values[0]),
        "temp": status_values[1],
        "volts": {
            "core": status_values[2],
            "sdram_c": status_values[3],
            "sdram_i": status_values[4],
            "sdram_p": status_values[5],
        },
    }


def get_status_value(row):
    return row.split("=")[-1]


def get_throttled_bit_status(hex_str):
    byte_string = "{0:b}".format(int(hex_str, 16))

    status = ""

    if byte_string[0] == "1":
        status.append("Under-voltage detected. ")
    if len(byte_string) > 3:
        if byte_string[1] == "1":
            status.append("Arm frequency capped. ")
        if byte_string[2] == "1":
            status.append("Currently throttled (slowed CPU). ")
        if byte_string[3] == "1":
            status.append("Soft temperature limit active. ")

    if len(byte_string) > 19:
        if byte_string[16] == "1":
            status.append("Under-voltage has occured. ")
        if byte_string[17] == "1":
            status.append("Arm frequency capped has occured. ")
        if byte_string[18] == "1":
            status.append("Throttling has occured. ")
        if byte_string[19] == "1":
            status.append("Soft temperature limit has occured. ")

    return status
