import * as controller from '../control'

const controls = {
  forward: controller.forward,
  reverse: controller.reverse,
  left: controller.left,
  right: controller.right,
  rot_left: controller.rotLeft,
  rot_right: controller.rotRight,
  stop: controller.stop,
  start_charging: controller.startCharging,
  stop_charging: controller.stopCharging,
}

export default message => controls[message]()

export const exit = () => controller.exit()
export const start = debug => controller.start(debug)
