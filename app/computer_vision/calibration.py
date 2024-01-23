from controller import run_motors
from computer_vision.cv_module import CVModule
from computer_vision import util
import cv2
import math


QR_WIDTH_MM = 63
START_DIST_MM = 460

# PHASES
START = "START"
DISTANCE = "DISTANCE"
ROTATION = "ROTATION"


class Calibration(CVModule):
    calibration_power = 0.4

    phase = START
    qr_readings = {DISTANCE: [], ROTATION: []}

    degrees_per_second_right = None
    millimeters_per_second = None
    focal_length = None

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def calibrate(self):
        super().activate()
        self.degrees_per_second_right = None

    def update(self, img):
        if not self.active:
            return

        if self.phase == START:
            self.phase_start(img)
        elif self.phase == DISTANCE:
            self.phase_distance(img)
        elif self.phase == ROTATION:
            self.phase_rotation(img)
        else:
            print("Calibration complete: ")
            print(self.get_calibration())
            super().deactivate()

        return

    def phase_start(self, img):
        box = self.detect_qr(img)
        if box is not None:
            self.qr_readings[DISTANCE].append(box)
            run_motors(-self.calibration_power, -self.calibration_power, 1)
            if len(self.qr_readings[DISTANCE]) > 0:
                self.phase = DISTANCE

    def phase_distance(self, img):
        box = self.detect_qr(img)
        if box is not None:
            self.qr_readings[DISTANCE].append(box)
            readings = self.qr_readings[DISTANCE]
            self.focal_length = util.calc_focal_length(
                START_DIST_MM, QR_WIDTH_MM, util.get_width(readings[0])
            )

            distance = self.get_millimeters_to_qr(box) - START_DIST_MM
            self.millimeters_per_second = distance
            self.phase = ROTATION

    def phase_rotation(self, img):
        box = self.detect_qr(img)
        if box is not None:
            if len(self.qr_readings[ROTATION]) == 0:
                self.qr_readings[ROTATION].append(box)
                run_motors(self.calibration_power, -self.calibration_power, 0.5)
            else:
                self.qr_readings[ROTATION].append(box)
                millimeters_to_qr = self.get_millimeters_to_qr(box)
                first_box_corner = self.qr_readings[ROTATION][0][3]
                second_box_corner = box[3]
                width_in_pixels = util.get_width(self.qr_readings[ROTATION][0])

                millimeter_per_pixel = QR_WIDTH_MM / width_in_pixels
                moved_horizontal_pixels = second_box_corner[0] - first_box_corner[0]

                moved_horizontal_millimeters = moved_horizontal_pixels * millimeter_per_pixel

                moved_degrees = math.atan2(moved_horizontal_millimeters, millimeters_to_qr)
                self.degrees_per_second_right = moved_degrees * 2
                self.phase = None

                print(f"Millimeters to qr before turn: {millimeters_to_qr}")
                print(f"width in pixels: {width_in_pixels}")
                print(f"Top left corner first reading: {first_box_corner}")
                print(f"Top left corner second reading: {second_box_corner}")
                print(f"Moved horiz pixels: {moved_horizontal_pixels}")
                print(f"Moved horiz millis: {moved_horizontal_millimeters}")
                print(f"Moved degrees: {moved_degrees}")

                

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
            "degrees_per_second_right": self.degrees_per_second_right,
            "seconds_per_degree_right": 1.0 / self.degrees_per_second_right
        }
