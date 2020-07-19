import * as controller from '../control'

export default socket => {
  socket.on('forward', controller.forward)
  socket.on('reverse', controller.reverse)
  socket.on('left', controller.left)
  socket.on('right', controller.right)
  socket.on('rotLeft', controller.rotLeft)
  socket.on('rotRight', controller.rotRight)
  socket.on('stop', controller.stop)
  socket.on('startCharging', controller.startCharging)
  socket.on('stopCharging', controller.stopCharging)
}

export const exit = () => controller.exit()
export const start = debug => controller.start(debug)
