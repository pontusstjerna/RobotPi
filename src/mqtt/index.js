import mqtt from 'mqtt'
import control, { start, exit } from './control'
import status from './status'
import { exec } from 'child_process'
import { config } from 'dotenv'

config()

const started = new Date().toString()
let idleTimeout = null
let lastConnected = null
let videoProcess = null

const {
  MQTT_BROKER_URL,
  MQTT_USERNAME,
  MQTT_PASSWORD,
  ID = 'robotpi',
  VIDEO_STREAM_HOST,
  VIDEO_STREAM_COMMAND = 'avconv -s 640x480 -f video4linux2 -i /dev/video0 -f mpegts -codec:v mpeg1video -codec:a mp2 -b 1000k',
  IDLE_TIMEOUT_MS = '300000',
} = process.env

export default () => {
  const debug = process.argv[2] === 'nopi'

  const mqttClient = mqtt.connect({
    hostname: MQTT_BROKER_URL || '127.0.0.1',
    username: MQTT_USERNAME,
    password: MQTT_PASSWORD,
    protocol: 'mqtt',
  })

  mqttClient.on('error', error => {
    console.log(error)
  })

  mqttClient.on('connect', () => {
    console.log(
      `"${ID}" connected to mqtt broker at ${process.env.MQTT_USERNAME}:${process.env.MQTT_BROKER_URL}`
    )

    mqttClient.subscribe(ID, error => {
      if (error) {
        console.log(error)
      } else {
        console.log(`Subscribed to "${ID}" topic with mqtt`)
      }
    })

    mqttClient.on('message', (topic, messageBuffer) => {
      if (!isRunning()) {
        console.log('Got message, will startup robot and video!')

        start(debug)
        if (!debug) {
          videoProcess = startVideoStreamProcess()
          console.log('Video stream started.')
        }
      }

      const message = messageBuffer.toString()

      setIdleTimeout()
      switch (message) {
        case 'started':
          mqttClient.publish(
            `${ID}/started`,
            JSON.stringify({ started, lastConnected })
          )
          break
        default:
          status(message, mqttClient, ID)
          control(message)
          break
      }
    })
  })

  return started
}

const isRunning = () => idleTimeout !== null

const setIdleTimeout = () => {
  if (idleTimeout !== null) {
    // Cancel old timeout on new message
    clearTimeout(idleTimeout)
  }

  idleTimeout = setTimeout(() => {
    // TODO: In the future, return to base?
    console.log('Five minutes idle, will turn off robot and video stream.')
    clearTimeout(idleTimeout)
    idleTimeout = null

    lastConnected = new Date().toString()

    if (videoProcess !== null) {
      videoProcess.kill()
    }
    videoProcess = null
    exit()
  }, parseInt(IDLE_TIMEOUT_MS) || 5 * 60 * 1000) // Keep alive for 5 minutes, then turn off
}

const startVideoStreamProcess = () => {
  const videoStreamUrl = `${VIDEO_STREAM_HOST}/video_stream/${ID}`
  const defaultCommand = `avconv -s 640x480 -f video4linux2 -i /dev/video0 -f mpegts -codec:v mpeg1video -codec:a mp2 -b 1000k ${videoStreamUrl}`

  return exec(
    `${VIDEO_STREAM_COMMAND} ${videoStreamUrl}` || defaultCommand,
    (error, stdout, stderr) => {
      console.log('Video streaming ended.')

      if (error != null) {
        console.log('Error with streaming: ' + error)
      }
    }
  )
}
