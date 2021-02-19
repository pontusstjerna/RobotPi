import express from 'express'
import http from 'http'
import connectMqtt from './mqtt'
import startVideoServer from './video'
import { config } from 'dotenv'

config()

const PORT = process.argv[3] || process.env.PORT || 4000

console.log('Starting server...')
const app = express()
const server = http.Server(app)
const started = connectMqtt()

server.listen(PORT, () => {
  startVideoServer(app, PORT)
  console.log(
    started + ': Websocket server successfully started on port ' + PORT
  )
})
