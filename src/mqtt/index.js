import mqtt from 'mqtt'
import control, { start, exit } from './control'
import status from './status'
import { startVideoStreamProcess } from '../localVideoStream'

const started = new Date().toString()
let idleTimeout = null
let lastConnected = null
let videoProcess = null

export default () => {
  const debug = process.argv[2] === 'nopi'

  const mqttClient = mqtt.connect({
    hostname: process.env.MQTT_BROKER_URL || '127.0.0.1',
    username: process.env.MQTT_USERNAME,
    password: process.env.MQTT_PASSWORD,
    protocol: 'mqtt',
  })

  mqttClient.on('connect', () => {
    console.log('Robotpi connected to mqtt broker')

    // TODO: Possibly use unique ID for robot (to allow more than one)
    mqttClient.subscribe('robotpi', error => {
      if (error) {
        console.log(error)
      } else {
        console.log('Subscribed to "robotpi" topic with mqtt')
      }
    })

    mqttClient.on('message', (topic, messageBuffer) => {
      if (!isRunning()) {
        console.log('Got message, will startup robot and video!')

        start(debug)
        if (!debug) {
          videoProcess = startVideoStreamProcess()
	  console.log("Video stream started.")
        }
      }

      const message = messageBuffer.toString()

      setIdleTimeout()
      switch (message) {
        case 'started':
          mqttClient.publish(
            'robotpi/started',
            JSON.stringify({ started, lastConnected })
          )
          break
        default:
          status(message, mqttClient)
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
  }, 5 * 60 * 1000) // Keep alive for 5 minutes, then turn off
}
