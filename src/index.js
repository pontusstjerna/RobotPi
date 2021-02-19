import express from 'express'
import http from 'http'
import connectMqtt from './mqtt'
import startVideoServer from './video'
import { config } from 'dotenv'

config()

console.log('Starting up...')
const started = connectMqtt()

// TODO: connect to ws for video streaming

/*server.listen(PORT, () => {
  startVideoServer(app, PORT)
  console.log(
    started + ': Websocket server successfully started on port ' + PORT
  )
})*/
