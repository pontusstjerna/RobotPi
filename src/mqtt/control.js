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
  set_power_low: () => controller.setPower(0.15),
  set_power_medium_low: () => controller.setPower(0.3),
  set_power_medium: () => controller.setPower(0.5),
  set_power_high: () => controller.setPower(1.0),
  tilt_camera_stop: controller.tiltCameraStop,
  tilt_camera_up: controller.tiltCameraUp,
  tilt_camera_down: controller.tiltCameraDown,
}

export default message => controls[message]?.()

export const exit = () => controller.exit()
export const start = debug => controller.start(debug)
