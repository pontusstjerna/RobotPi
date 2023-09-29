from multiprocessing import Process
import os
import cv2
from vidgear.gears import WriteGear
import time
from qr_follower import QrFollower
from controller import set_motors

try:
    from INA260_bridge import get_voltage, get_current
except NotImplementedError:
    print("Not access to Raspberry PI, skipping INA260 import")


output_params = {
    "-input_framerate": "30",
    "-f": "mpegts",
    "-r": "30",
    "-vcodec": "mpeg1video",
    "-b:v": "1000k",
}


def resize_img(img, scale=0.3):
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    return cv2.resize(img, (width, height))


class VideoProcessor:
    running = False

    def __init__(self, is_debug):
        self.is_debug = is_debug

    def start(self):
        print("Initiating camera stream...")

        # set up camera object
        self.cap = cv2.VideoCapture(0)
        self.qr_follower = QrFollower()

        # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.writer = WriteGear(
            output=f"{os.environ.get('VIDEO_STREAM_HOST')}/video_stream/robotpi",
            compression_mode=True,
            logging=True,
            **output_params,
        )

        self.running = True

    def stop(self):
        self.running = False
        self.writer.close()

    def update(self):
        if not self.running:
            time.sleep(1)
            return

        _, img = self.cap.read()
        self.qr_follower.update(img)
        self.display_voltage(img)
        self.writer.write(img)

    def follow_qr(self):
        self.follow_qr = True

    def stop_follow_qr(self):
        self.follow_qr = False

    def display_voltage(self, img):
        height, _, _ = img.shape

        if not self.is_debug:
            cv2.putText(
                img,
                f"Voltage: {get_voltage()}",
                (0, height - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        text = (
            f"Current: {get_current()}"
            if not self.is_debug
            else "DEBUG MODE - NO VOLTAGE AVAILABLE"
        )
        cv2.putText(
            img,
            text,
            (0, height - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
