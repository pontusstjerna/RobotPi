import express from 'express'
import http from 'http'

import socket from './socket'
import startVideoServer from './video'

const PORT = process.argv[3] || 4000

console.log('Starting server...')
const app = express()
const server = http.Server(app)
const started = socket(server)

server.listen(4000, () => {
  startVideoServer(app, PORT)
  console.log(started + ': Websocket server successfully started on port ' + PORT)
})
