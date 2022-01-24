import subprocess


def get_status(controller):
    # Example result: b"throttled=0x0\ntemp=44.0'C\nvolt=1.2875V\nvolt=1.2000V\nvolt=1.2000V\nvolt=1.2250V\n"
    status_string = subprocess.check_output(["sh", "get_status.sh"])

    return {"power": controller.power}
