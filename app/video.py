import os
import cv2
from vidgear.gears import WriteGear
import time
from computer_vision.qr_follower import QrFollower
from computer_vision.cv_module import CVModule

output_params = {
    "-input_framerate": "20",
    "-f": "mpegts",
    "-r": "20",
    "-vcodec": "mpeg1video",
    "-fflags": "nobuffer",
    "-b:v": "1000k",
}


def resize_img(img, scale=0.3):
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    return cv2.resize(img, (width, height))


class VideoProcessor:
    running = False
    cv_modules: [CVModule] = []

    def start(self):
        print("Initiating camera stream...")

        # set up camera object
        self.cap = cv2.VideoCapture(0)
        W, H = 1920, 1080
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G"))
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.writer = WriteGear(
            output=f"{os.environ.get('VIDEO_STREAM_HOST')}/video_stream/robotpi",
            compression_mode=True,
            logging=False,
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

        for module in self.cv_modules:
            module.update(img)

        self.writer.write(img)

    def add_cv_module(self, module: CVModule):
        self.cv_modules.append(module)

    def remove_cv_module(self, module: CVModule):
        self.cv_modules.remove(module)