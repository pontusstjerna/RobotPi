from math import isqrt
import os
import cv2
from controller import set_motors


def get_dist(a, b):
    return isqrt(int(pow(b[0] - a[0], 2)) + int(pow(b[1] - a[1], 2)))


qr_dock_text = os.environ.get("QR_DOCK_TEXT") or "robotpi-dock"
qr_follow_text = os.environ.get("QR_FOLLOW_TEXT") or "robotpi-follow"
follow_proximity_margin = 50
stop_diagonal_len = 150
min_diagonal_len = 50


class QrCodeFollower:
    running = False
    found_qr = False
    diagonal_len = -1

    def start(self):
        print(f"Following QR code")
        self.running = True

        # set up camera object
        cap = cv2.VideoCapture(0)

        # QR code detection object
        detector = cv2.QRCodeDetector()

        while self.running:
            # get the image
            _, img = cap.read()

            bounding_box = None

            if not self.found_qr:
                # get bounding box coords and data
                # data, bounding_box, _ = detector.detectAndDecode(img)
                data, _, _ = detector.detectAndDecode(img)

                self.found_qr = data == qr_dock_text or data == qr_follow_text
            else:
                bounding_box, _ = detector.detect(img)

            height, width, _ = img.shape
            max_diag = get_dist([0, 0], [width, height])

            # if there is a bounding box, draw one, along with the data
            if bounding_box is not None and self.found_qr:
                points = bounding_box[0]
                top_left_corner = points[0]
                top_right_corner = points[1]
                diagonal_len = get_dist(points[0], points[2])

                portion_of_img = diagonal_len / max_diag

                print(f"Data: {data}")
                # print(f"Center point: {top_left_corner}")
                # print(f"Width: {width}, Height: {height}")

                print(
                    f"{'top' if top_left_corner[1] < height / 2 else 'bottom'} {'left' if top_left_corner[0] < width / 2 else 'right'}"
                )

                pwr = portion_of_img
                print(f"diag_len: {diagonal_len}")
                print(f"Pwr: {pwr}")
                if top_left_corner[0] < width / 3:
                    set_motors(-pwr, pwr)
                elif top_left_corner[0] > width * 2 / 3:
                    set_motors(pwr, -pwr)
                else:
                    set_motors(pwr, pwr)
            else:
                set_motors(0, 0)


        # free camera object and exit
        cap.release()

    def stop(self):
        self.running = False
        self.found_qr = False
