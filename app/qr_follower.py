from math import isqrt
import cv2
from controller import set_motors


def get_dist(a, b):
    return isqrt(int(pow(b[0] - a[0], 2)) + int(pow(b[1] - a[1], 2)))


follow_proximity_margin = 50
stop_diagonal_len = 150
min_diagonal_len = 50
max_no_reading_count = 10
min_diagonal_len_delta = 50


class QrFollower:
    last_center_point = (0, 0)
    follow_qr = False

    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def follow(self):
        self.follow_qr = True

    def stop_follow(self):
        self.follow_qr = False

    def update(self, img):
        _, boxes = self.detector.detect(img)
        height, width, _ = img.shape

        if boxes is not None:
            box = boxes[0]
            diagonal_length = get_dist(box[0], box[1])
            center_point = (
                int(box[0][0]) - int(diagonal_length / 2),
                int(box[0][1]) + int(diagonal_length / 2),
            )
            img_horizontal_center = int(width / 2)

            status = f"DIAG: {diagonal_length}px"

            # Remove misreadings
            if get_dist(self.last_center_point, center_point) < min_diagonal_len_delta:
                for i in range(len(box)):
                    cv2.line(
                        img,
                        tuple(box[i].astype(int)),
                        tuple(box[(i + 1) % len(box)].astype(int)),
                        color=(150, 255, 150),
                        thickness=2,
                    )
                    cv2.circle(
                        img, center_point, 10, color=(150, 255, 150), thickness=2
                    )

                if self.follow_qr:
                    turn_factor = (2 * center_point[0] / width) - 1
                    status = f"{status}, TF: {round(turn_factor, 2)}"

                    # set_motors(turn_factor, -turn_factor)
            cv2.putText(
                img,
                status,
                (0, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            self.last_center_point = center_point

            # else:
            # set_motors(0, 0)

            # pwr = 0.3

            # if len(qr_reading) > 0:
            #     no_reading_count = 0
            #     decoded = qr_reading[0]
            #     diagonal = get_dist(decoded.polygon[0], decoded.polygon[2])

            #     movement_of_freedom = width - decoded.rect.width

            #     # 0 left, 0.5 forward, 1.0 right
            #     turn = decoded.rect.left / movement_of_freedom

            #     # print(turn)
            #     set_motors(turn, -turn)

            # else:
            #     no_reading_count += 1
            #     if no_reading_count >= max_no_reading_count:
            #         no_reading_count = 0
            #         print("Stopping.")
            #         set_motors(0, 0)
