import { exec } from 'child_process'

export const startVideoStreamProcess = port => {
  const defaultCommand = `avconv -s 640x480 -f video4linux2 -i /dev/video0 -f mpegts -codec:v mpeg1video -codec:a mp2 -b 1000k ${process.env.VIDEO_STREAMING_URL}`

  return exec(
    process.env.VIDEOO_STREAM_COMMAND || defaultCommand,
    (error, stdout, stderr) => {
      console.log('Video streaming started.')

      if (error != null) {
        console.log('Error with streaming: ' + error)
      }
    }
  )
}
