import connectMqtt from './mqtt'
import { config } from 'dotenv'

config()

const started = connectMqtt()
console.log(`Cat Hunter started mqtt at ${started}`)

// TODO: connect to ws for video streaming

/*server.listen(PORT, () => {
  startVideoServer(app, PORT)
  console.log(
    started + ': Websocket server successfully started on port ' + PORT
  )
})*/
