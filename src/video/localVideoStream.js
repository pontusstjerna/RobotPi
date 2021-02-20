export const startVideoStreamProcess = port => {
  return exec(
    `avconv -s 640x480 -f video4linux2 -i /dev/video0 -f mpegts -codec:v mpeg1video -codec:a mp2 -b 1000k ${process.env.VIDEO_STREAMING_URL}`,
    (error, stdout, stderr) => {
      console.log(stdout)
      console.log(stderr)

      if (error != null) {
        console.log('Error with streaming: ' + error)
      }
    }
  )
}
