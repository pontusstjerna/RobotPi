from controller import run_motors
from computer_vision.cv_module import CVModule
from computer_vision import util
import cv2


QR_WIDTH_MM = 70
START_DIST_MM = 460

# PHASES
START = "START"
DISTANCE = "DISTANCE"


class Calibration(CVModule):
    calibration_power = 0.4

    phase = START
    qr_readings = {DISTANCE: []}

    degrees_per_second = None
    millimeters_per_second = None
    focal_length = None

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def calibrate(self):
        super().activate()
        self.degrees_per_second = None

    def update(self, img):
        if not self.active:
            return

        if self.phase == START:
            self.phase_start(img)
        elif self.phase == DISTANCE:
            self.phase_distance(img)

        return

    def phase_start(self, img):
        box = self.detect_qr(img)
        if box is not None:
            self.qr_readings[DISTANCE].append(box)
            run_motors(-self.calibration_power, -self.calibration_power, 1)
            if len(self.qr_readings[DISTANCE]) >= 2:
                self.phase = DISTANCE

    def phase_distance(self, img):
        box = self.detect_qr(img)
        if box is not None:
            self.qr_readings[DISTANCE].append(box)
            readings = self.qr_readings[DISTANCE]
            self.focal_length = util.calc_focal_length(
                START_DIST_MM, QR_WIDTH_MM, util.get_width(readings[0])
            )

            distances = [self.get_millimeters_to_qr(box) for box in readings]
            self.millimeters_per_second = sum(distances) / len(distances)
            self.phase = None
            print("Calibration complete: ")
            print(self.get_calibration())
            super().deactivate()

    def detect_qr(self, img):
        _, boxes = self.detector.detect(img)
        if boxes is not None:
            return boxes[0]

    def get_millimeters_to_qr(self, box):
        return util.calc_dist(self.focal_length, QR_WIDTH_MM, util.get_width(box))

    def get_calibration(self):
        return {
            "power": self.calibration_power,
            "millimeters_per_second": self.millimeters_per_second,
            "seconds_per_millimenter": 1.0 / self.millimeters_per_second,
        }
