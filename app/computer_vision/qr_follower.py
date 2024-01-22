from math import isqrt
import cv2
from controller import set_motors
import config

from computer_vision.cv_module import CVModule

max_diagonal_len = 450
min_line_up_diagonal_len = 200
max_line_up_diagonal_len = 250
min_diagonal_len_delta = 50
turn_factor_threshold = 0.1
update_interval = 3
pwr = 0.5

# BEARING
RIGHT = "RIGHT"
LEFT = "LEFT"
IN_FRONT = "IN_FRONT"

# PHASES
SEARCHING = "SEARCHING"
FOLLOWING = "FOLLOWING"
LINING_UP = "LINING_UP"
ARRIVED = "ARRIVED"


class QrFollower(CVModule):
    last_center_point = (0, 0)
    frames_since_move = 0
    last_seen = RIGHT
    phase = SEARCHING

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def activate(self):
        # Search for QR, starting to the right
        self.last_seen = RIGHT
        super().activate()

    def update(self, img):

        if not self.active:
            return

        status = f"Phase: {self.phase}"

        # Wait couple frames after move to tackle blurry images
        if self.frames_since_move < update_interval:
            if self.frames_since_move > 0:
                self.set_motors(0, 0, img)
            self.frames_since_move += 1
            return

        _, boxes = self.detector.detect(img)

        if boxes is None and self.phase != ARRIVED and self.phase != LINING_UP:
            self.phase = SEARCHING
        elif boxes is not None:
            box = boxes[0]
            diagonal_length = get_dist(box[0], box[2])
            status += f", DIAG: {diagonal_length}"
            if diagonal_length >= max_diagonal_len:
                self.phase = ARRIVED
            elif (
                self.phase == FOLLOWING
                and diagonal_length >= min_line_up_diagonal_len
                and diagonal_length <= max_diagonal_len
            ):
                self.phase = LINING_UP
            elif self.phase == SEARCHING:
                self.phase = FOLLOWING

        self.act_on_phase(img, None if boxes is None else boxes[0])
        self.print_status(img, status)

    def act_on_phase(self, img, box):
        if self.phase == SEARCHING:
            self.find_qr(img)
        elif self.phase == FOLLOWING:
            diagonal_length = get_dist(box[0], box[2])
            right_side_len = get_dist(box[0], box[1])
            left_side_len = get_dist(box[2], box[3])
            top_side_len = get_dist(box[3], box[0])

            center_point = (
                int(box[0][0]) - int(top_side_len / 2),
                int(box[0][1]) + int(top_side_len / 2),
            )

            has_moved_not_so_much = (
                get_dist(self.last_center_point, center_point) < min_diagonal_len_delta
            )

            # Remove misreadings
            if has_moved_not_so_much:
                self.print_qr_graphics(img, box, center_point)
                self.follow_qr(img, center_point, diagonal_length)

            self.last_center_point = center_point
        elif self.phase == LINING_UP:
            self.line_up(img, box)

    def follow_qr(self, img, center_point, diagonal_len):
        width = img.shape[1]
        turn_factor = (0 + 2 * center_point[0] / width) - 1
        arrived = diagonal_len >= max_diagonal_len

        if turn_factor < -turn_factor_threshold and not arrived:
            self.last_seen = RIGHT
            self.set_motors(-pwr, pwr, img)
        elif turn_factor > turn_factor_threshold and not arrived:
            self.last_seen = LEFT
            self.set_motors(pwr, -pwr, img)
        elif not arrived:
            self.last_seen = IN_FRONT
            self.set_motors(pwr * 0.7, pwr * 0.7, img)
        else:
            self.last_seen = None
            self.set_motors(0, 0, img)

    def find_qr(self, img):
        if self.last_seen == RIGHT:
            self.set_motors(pwr, -pwr, img)
        elif self.last_seen == LEFT:
            self.set_motors(-pwr, pwr, img)
        elif self.last_seen == IN_FRONT:
            self.set_motors(-pwr * 0.7, -pwr * 0.7, img)

    def lineup(self, img, box):
        self.set_motors(0, 0, img)

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
