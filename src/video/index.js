import io from 'socket.io-client'
import express from 'express'
import http from 'http'

// TODO: Add token
export default videoPort => {
  const app = express()
  const videoServer = http.Server(app)

  const socket = io('/video_input')

  app.use('/stream', (request, response) => {
    response.connection.setTimeput(0)
    console.log('Local video stream connected.')

    // Local stream of data is received, send to main server
    request.on('data', data => socket.emit('video_data', data))

    request.on('end', () => console.log('Local video stream ended'))
  })

  videoServer.listen(videoPort, () => {
    console.log('Http server for local video streaming')
  })
}
