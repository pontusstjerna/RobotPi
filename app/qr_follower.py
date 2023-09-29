from math import isqrt
import cv2
from controller import set_motors
import time


def get_dist(a, b):
    return isqrt(int(pow(b[0] - a[0], 2)) + int(pow(b[1] - a[1], 2)))


follow_proximity_margin = 50
stop_diagonal_len = 150
max_diagonal_len = 450
max_no_reading_count = 10
min_diagonal_len_delta = 50
turn_factor_threshold = 0.1
pwr = 0.35


class QrFollower:
    last_center_point = (0, 0)
    follow_qr = True
    has_moved = False

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def follow(self):
        self.follow_qr = True

    def stop_follow(self):
        self.follow_qr = False

    def update(self, img):
        if self.has_moved:
            self.has_moved = False
            return

        _, boxes = self.detector.detect(img)
        height, width, _ = img.shape

        if boxes is not None:
            box = boxes[0]
            diagonal_length = get_dist(box[0], box[2])
            right_side_len = get_dist(box[0], box[1])
            left_side_len = get_dist(box[2], box[3])
            top_side_len = get_dist(box[3], box[0])

            side_len_delta = left_side_len - right_side_len

            center_point = (
                int(box[0][0]) - int(top_side_len / 2) + side_len_delta * 10,
                int(box[0][1]) + int(top_side_len / 2),
            )

            status = f"DIAG: {diagonal_length}px"
            has_moved_not_so_much = (
                get_dist(self.last_center_point, center_point) < min_diagonal_len_delta
            )

            # Remove misreadings
            if has_moved_not_so_much:
                self.print_qr_graphics(img, box, center_point)

                if self.follow_qr:
                    self.follow_qr(img, center_point, diagonal_length)
            else:
                set_motors(0, 0)

            self.print_status(img, status)
            self.last_center_point = center_point
        else:
            self.print_set_motors(img, 0, 0)
            set_motors(0, 0)

    def follow_qr(self, img, center_point, diagonal_len):
        width = img.shape[1]
        turn_factor = (0 + 2 * center_point[0] / width) - 1
        self.has_moved = True
        arrived = diagonal_len >= max_diagonal_len

        if turn_factor < -turn_factor_threshold and not arrived:
            self.print_set_motors(img, -pwr, pwr, "LEFT")
            set_motors(-pwr, pwr)
        elif turn_factor > turn_factor_threshold and not arrived:
            self.print_set_motors(img, pwr, -pwr, "RIGHT")
            set_motors(pwr, -pwr)
        elif not arrived:
            self.print_set_motors(img, pwr, pwr, "FORWARD")
            set_motors(pwr * 0.7, pwr * 0.7)
        else:
            self.print_set_motors(img, 0, 0, "STOPPING")
            set_motors(0, 0)

    def print_qr_graphics(self, img, box, center_point):
        cv2.line(
            img,
            tuple(box[0].astype(int)),
            tuple(box[1].astype(int)),
            color=(150, 255, 150),
            thickness=2,
        )

        cv2.line(
            img,
            tuple(box[2].astype(int)),
            tuple(box[3].astype(int)),
            color=(150, 150, 255),
            thickness=2,
        )

        cv2.circle(img, center_point, 10, color=(150, 255, 150), thickness=2)

    def print_status(self, img, status):
        cv2.putText(
            img,
            status,
            (0, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def print_set_motors(self, img, left, right, msg=None):
        cv2.putText(
            img,
            f"LEFT: {round(left, 2)}, RIGHT: {round(right, 2)}, {msg or ''}",
            (0, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
