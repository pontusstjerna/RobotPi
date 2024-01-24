from math import isqrt
import cv2
from controller import run_motors
import config
from computer_vision.util import get_dist, get_width
from computer_vision import util

from computer_vision.cv_module import CVModule

PWR = 0.3
MAX_DIAGONAL_LEN = 200
LINE_UP_THRESHOLD_DIAGONAL_LENGTH = 150

# PHASES
SEARCHING = "SEARCHING"
CENTRALIZE = "CENTRALIZE"
FOLLOWING = "FOLLOWING"
LINING_UP = "LINING_UP"
ARRIVED = "ARRIVED"


class QrFollower(CVModule):
    frames_since_move = 0
    phase = SEARCHING

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def activate(self):
        super().activate()
        self.phase = SEARCHING

    def update(self, img):
        if not self.active:
            return

        status = f"Phase: {self.phase}"
        if self.phase == SEARCHING:
            self.phase_searching(img)
        elif self.phase == CENTRALIZE:
            self.phase_lining_up(img)
        elif self.phase == FOLLOWING:
            self.phase_follow()
        elif self.phase == LINING_UP:
            self.phase_lining_up(img)
        else:
            print("Following complete!")
            super().deactivate()

        self.print_status(img, status)

    def phase_lining_up(self, img):
        box = self.detect_qr(img)
        if box is not None:
            if util.get_diagonal_length(box) > MAX_DIAGONAL_LEN:
                print("Done!")
                self.phase = None
            else:
                right_side_len = get_dist(box[0], box[1])
                left_side_len = get_dist(box[2], box[3])

                if abs(right_side_len - left_side_len) < 4:
                    run_motors(PWR, PWR, 0.3)
                elif right_side_len > left_side_len:  # go left
                    run_motors(PWR, -PWR, 0.5)
                    run_motors(-PWR, -PWR, 0.5)
                    run_motors(-PWR, PWR, 0.5)
                    self.phase = SEARCHING
                else:  # go right
                    run_motors(-PWR, PWR, 0.5)
                    run_motors(-PWR, -PWR, 0.5)
                    run_motors(PWR, -PWR, 0.5)
                    self.phase = SEARCHING

    def phase_searching(self, img):
        box = self.detect_qr(img)
        if box is not None:
            self.phase = CENTRALIZE
        elif self.frames_since_move > 5:
            self.frames_since_move = 0
            run_motors(PWR, -PWR, 0.5)
        else:
            self.frames_since_move += 1

    def phase_centralize(self, img):
        box = self.detect_qr(img)
        if box is not None:
            turn_factor = self.calc_turn_factor(img, util.calc_center_point(box))
            if turn_factor > 0.2:
                run_motors(-PWR, PWR, 0.2)
            elif turn_factor < -0.2:
                run_motors(PWR, -PWR, 0.2)
            else:
                if util.get_diagonal_length(box) < LINE_UP_THRESHOLD_DIAGONAL_LENGTH:
                    self.phase = FOLLOWING
                else:
                    self.phase = LINING_UP

    def phase_follow(self):
        run_motors(PWR, PWR, 0.3)
        self.phase = CENTRALIZE

    def print_qr_graphics(self, img, box, center_point):
        # Right side
        cv2.line(
            img,
            tuple(box[0].astype(int)),
            tuple(box[1].astype(int)),
            color=(100, 100, 255),
            thickness=2,
        )

        cv2.line(
            img,
            tuple(box[2].astype(int)),
            tuple(box[3].astype(int)),
            color=(100, 255, 100),
            thickness=2,
        )

        cv2.circle(img, center_point, 10, color=(150, 255, 150), thickness=2)

    def set_motors(self, left, right, img):
        if not (left == 0 and right == 0):
            self.frames_since_move = 0

        msg = "STOPPING"
        if left < right:
            msg = LEFT
        elif right < left:
            msg = RIGHT
        elif left == right and left > 0:
            msg = "FORWARD"

        cv2.putText(
            img,
            f"LEFT: {round(left, 2)}, RIGHT: {round(right, 2)}, {msg}",
            (0, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        if not config.IS_DEBUG:
            set_motors(left, right)

    def calc_turn_factor(self, img, center_point):
        width = img.shape[1]
        return (2 * center_point[0] / width) - 1

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

    def detect_qr(self, img):
        _, boxes = self.detector.detect(img)
        if boxes is not None:
            return boxes[0]
