from .cv_module import CVModule
import util

class ChargingQrData(CVModule):

#    def __init__(self):
    data = {
        "left_side": None,
        "right_side": None,
        "center_x": None,
        "center_y": None
    }

    def update(self, img):
        util