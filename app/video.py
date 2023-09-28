from math import isqrt
from multiprocessing import Process
import os
import cv2
import time
import sys
from vidgear.gears import WriteGear
from controller import set_motors
from INA260_bridge import get_voltage, get_current


def get_dist(a, b):
    return isqrt(int(pow(b[0] - a[0], 2)) + int(pow(b[1] - a[1], 2)))


qr_dock_text = os.environ.get("QR_DOCK_TEXT") or "robotpi-dock"
qr_follow_text = os.environ.get("QR_FOLLOW_TEXT") or "robotpi-follow"
follow_proximity_margin = 50
stop_diagonal_len = 150
min_diagonal_len = 50
max_no_reading_count = 10
min_diagonal_length_delta = 100

video_stream_host = os.environ.get("VIDEO_STREAM_HOST")
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
    following_qr = False
    last_center_point = (0, 0)

    def start(self):
        if self.running:
            return
        self.running = True
        self.process = Process(target=self.start_camera)
        self.process.start()

    def stop(self):
        self.stop_follow_qr()
        self.running = False
        self.process = None

    def follow_qr(self):
        self.follow_qr = True

    def stop_follow_qr(self):
        self.follow_qr = False

    def display_voltage(self, img):
        height, _, _ = img.shape
        cv2.putText(
            img,
            f"Voltage: {get_voltage()}",
            (0, height - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            img,
            f"Current: {get_current()}",
            (0, height - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    def start_camera(self):
        print("Starting camera stream")

        # set up camera object
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        writer = WriteGear(
            output=f"{video_stream_host}/video_stream/picam2",
            compression_mode=True,
            logging=True,
            **output_params,
        )

        no_reading_count = 0

        while self.running:
            # get the image
            _, img = cap.read()

            height, width, _ = img.shape
            status = "QR"

            _, boxes = detector.detect(img)

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
                if (
                    get_dist(self.last_center_point, center_point)
                    < min_diagonal_length_delta
                ):
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

                        set_motors(turn_factor, -turn_factor)

                    cv2.putText(
                        img,
                        status,
                        (0, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )

                    self.display_voltage()
                else:
                    set_motors(0, 0)

                self.last_center_point = center_point

            writer.write(img)

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
        cv2.destroyAllWindows()
        img.release()
        writer.close()


if __name__ == "__main__":
    vid = VideoProcessor()
    vid.start()
