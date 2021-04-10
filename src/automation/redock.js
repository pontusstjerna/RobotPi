import * as controller from '../control'

export default () => {
  const intervalMins = process.env.REDOCK_INTERVAL_MINUTES || 60
  setInterval(() => {
    controller.start(process.argv[2] === 'nopi')
    redock(controller)
    clearTimeout(timeout)
    controller.exit()
  }, intervalMins /* * 60*/)
}

const redock = () => {
  const oldPower = controller.getPower()
  controller.setPower(0.2)
  controller.reverse()

  forOneSecond(controller.forward)
    .then(() =>
      forOneSecond(() => {
        controller.reverse()
        controller.forward()
      })
    )
    .then(forOneSecond(controller.stop))
    .then(controller.setPower(oldPower))
}

const forOneSecond = action =>
  new Promise(resolve =>
    setTimeout(() => {
      action()
      resolve()
    }, 1000)
  )
