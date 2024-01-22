from controller import run_motors
from computer_vision.cv_module import CVModule
import cv2


QR_WIDTH_MM = 70

# PHASES
START = "START"
ROTATION = "ROTATION"


class Calibration(CVModule):
    calibration_power = 0.4

    phase = START
    qr_readings = {START: []}

    degrees_per_second = None

    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        return

    def calibrate(self):
        super().activate(True)
        self.degrees_per_second = None

    def update(self, img):
        if not self.active:
            return

        if self.phase == START:
            self.phase_start(img)

        return

    def phase_start(self, img):
        box = self.detect_qr(img)
        if box is not None:
            run_motors(-self.calibration_power, -self.calibration_power, 1)
            self.phase = 

    def detect_qr(self, img):
        _, boxes = self.detector.detect(img)
        if boxes is not None:
            return boxes[0]
