import connectMqtt from './mqtt'
import startRedockInterval from './automation/redock'

connectMqtt().then(started => {
  console.log(`Cat Hunter started at ${started}`)
  startRedockInterval()
})
