import subprocess
import os


def start_video_stream_process():
    video_stream_host = os.environ.get("VIDEO_STREAM_HOST")
    if video_stream_host:
        print("Starting video stream.")
        return subprocess.Popen(
            f"exec ffmpeg -s 640x480 -f video4linux2 -i /dev/video0 -f mpegts -codec:v mpeg1video -codec:a mp2 -b 1000k {video_stream_host}/video_stream/robotpi",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
    else:
        print("Missing config: VIDEO_STREAM_HOST")
