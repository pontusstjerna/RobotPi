import WebSocket from 'ws'
import { exec } from 'child_process'
import sys from 'util'

let childProcess = null

export default (app, basePort) => {
  const WEBSOCKET_PORT = parseInt(basePort) + 2

  const streamingSocketServer = new WebSocket.Server({
    port: WEBSOCKET_PORT,
    perMessageDeflate: false,
  })
  streamingSocketServer.connectionCount = 0
  streamingSocketServer.on('connection', (socket, upgradeReq) => {
    if (process.argv[2] !== 'nopi' && childProcess === null) {
      childProcess = startVideoStreamProcess(basePort)
      console.log('First video socket, starting video stream.')
    }

    streamingSocketServer.connectionCount++
    console.log(
      'Video listener connected. ' +
        streamingSocketServer.connectionCount +
        ' sockets connected.'
    )

    socket.on('close', () => {
      streamingSocketServer.connectionCount--

      console.log(
        'Video listener disconnected (' +
          streamingSocketServer.connectionCount +
          ' total)'
      )
      if (
        streamingSocketServer.connectionCount === 0 &&
        childProcess !== null
      ) {
        console.log('Last video socket disconnected; killing video stream.')
        childProcess.kill()
        childProcess = null
      }
    })
  })

  // Broadcast video stream
  streamingSocketServer.broadcast = function (data) {
    streamingSocketServer.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data)
      }
    })
  }

  // Receive local video stream
  app.use('/stream', (request, response) => {
    response.connection.setTimeout(0)
    console.log('Local video stream connected.')

    // Local stream of data is received, broadcast to all listeners
    request.on('data', data => {
      streamingSocketServer.broadcast(data)

      // Don't know that this does
      if (request.socket.recording) {
        request.socket.recording.write(data)
      }
    })

    request.on('end', () => {
      console.log('Local video stream closed')

      if (request.socket.recording) {
        request.socket.recording.close()
      }
    })
  })

  console.log(
    'Listening for incoming MPEG-TS stream through websocket on localhost:' +
      basePort +
      '/stream'
  )
  console.log(
    'Awaiting video listeners on websocket connections on ws://localhost:' +
      WEBSOCKET_PORT
  )
}

const startVideoStreamProcess = port => {
  return exec(
    `avconv -s 640x480 -f video4linux2 -i /dev/video0 -f mpegts -codec:v mpeg1video -codec:a mp2 -b 1000k http://localhost:${port}/stream`,
    (error, stdout, stderr) => {
      //sys.print('stout: ' + stdout);
      //sys.print('stderr: ' + stder);
      console.log(stdout)
      console.log(stderr)

      if (error != null) {
        console.log('Error with streaming: ' + error)
      }
    }
  )
}
