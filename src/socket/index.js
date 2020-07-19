import socketIO from 'socket.io'
import control, { start, exit } from './control.js'
import status from './status'
import { exec } from 'child_process'

const started = new Date().toString()
let users = 0
let lastConnected = null

export default server => {
  const io = socketIO(server)

  io.on('connection', socket => {
    console.log('User connected.')

    // TODO: Not thread safe
    users++
    if (users === 1) {
      start(process.argv[2] === 'nopi')
    }

    socket.on('started', () => {
      console.log('Got started from client')
      socket.emit('started', JSON.stringify({ started, lastConnected }))
    })

    // Handle system status updates
    status(socket)

    // Setup controller parts
    control(socket)

    socket.on('disconnect', () => {
      console.log('User disconnected')
      users--
      lastConnected = new Date().toString()
      if (users === 0) {
        exit()
      }
    })
  })

  return started
}
