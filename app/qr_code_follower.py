from math import isqrt
import os
import cv2
from controller import set_motors

def get_dist(a, b):
    return isqrt(int(pow(b[0] - a[0], 2)) + int(pow(b[1] - a[1], 2)))

qr_dock_text = os.environ.get("QR_DOCK_TEXT") or "robotpi-dock"
qr_follow_text = os.environ.get("QR_FOLLOW_TEXT") or "robotpi-follow"
follow_proximity_margin = 50
min_diagonal_len = 50

class QrCodeFollower:
    running = False
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
            # get bounding box coords and data
            data, bounding_box, _ = detector.detectAndDecode(img)

            height, width, _ = img.shape

            #if there is a bounding box, draw one, along with the data
            if bounding_box is not None and data is not None:
                points = bounding_box[0]
                top_left_corner = points[0]
                top_right_corner = points[1]
                diagonal_len = get_dist(points[0], points[2])
                
                print("Data: {data}")
                print(f"Center point: {top_left_corner}")
                print(f"Width: {width}, Height: {height}")

                print(f"{'top' if top_left_corner[1] < height / 2 else 'bottom'} {'left' if top_left_corner[0] < width / 2 else 'right'}")

                if data == qr_dock_text or data == qr_follow_text:
                    if self.diagonal_len == -1:
                        self.diagonal_len = diagonal_len
                    
                    forward_pwr = 1
                    if (diagonal_len + follow_proximity_margin) < self.diagonal_len: # QR code appears smaller -> go forward!
                        set_motors(0.3, 0.3)    
                    elif (diagonal_len - follow_proximity_margin) > self.diagonal_len and data == qr_follow_text: # Go backward only if follow mode is on
                        set_motors(0, 0)
                    else:
                        set_motors(0, 0)
                
        # free camera object and exit
        cap.release()

    def stop(self):
        self.running = False
