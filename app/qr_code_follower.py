from math import isqrt
from multiprocessing import Process
import os
import cv2
from pyzbar import pyzbar
from controller import set_motors


def get_dist(a, b):
    return isqrt(int(pow(b[0] - a[0], 2)) + int(pow(b[1] - a[1], 2)))


qr_dock_text = os.environ.get("QR_DOCK_TEXT") or "robotpi-dock"
qr_follow_text = os.environ.get("QR_FOLLOW_TEXT") or "robotpi-follow"
follow_proximity_margin = 50
stop_diagonal_len = 150
min_diagonal_len = 50
max_no_reading_count = 10

def resize_img(img, scale=0.3):
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    return cv2.resize(img, (width, height))

class QrCodeFollower:
    running = False
    found_qr = False
    diagonal_len = -1

    def start(self):
        self.running = True
        self.process = Process(target=self.__follow)
        self.process.start()

    def stop(self):
        self.running = False

    def __follow(self):
        print(f"Following QR code")

        # set up camera object
        cap = cv2.VideoCapture(0)

        no_reading_count = 0

        while self.running:
            # get the image
            _, img = cap.read()
            img = resize_img(img, 0.5)

            height, width, _ = img.shape

            # Example
            # [Decoded(data=b'Hej', type='QRCODE', rect=Rect(left=343, top=224, width=78, height=75), polygon=[Point(x=343, y=229), Point(x=348, y=299), Point(x=421, y=294), Point(x=413, y=224)], quality=1, orientation='UP')]
            qr_reading = pyzbar.decode(img)

            pwr = 0.3

            if len(qr_reading) > 0:
                no_reading_count = 0
                decoded = qr_reading[0]
                diagonal = get_dist(decoded.polygon[0], decoded.polygon[2])
                
                movement_of_freedom = width - decoded.rect.width

                # 0 left, 0.5 forward, 1.0 right
                turn = decoded.rect.left / movement_of_freedom
            
                #print(turn)
                set_motors(turn, -turn)

            else:
                no_reading_count += 1
                if no_reading_count >= max_no_reading_count:
                    no_reading_count = 0
                    print("Stopping.")
                    set_motors(0, 0)
    