import * as controller from '../control'

export default () => {
  const intervalMins = process.env.REDOCK_INTERVAL_MINUTES || 60
  setInterval(() => {
    controller.start(process.argv[2] === 'nopi')
    redock() //.then(controller.exit)
  }, intervalMins * 1000 /* * 60*/)
}

const redock = () =>
  new Promise(resolve => {
    const oldPower = controller.getPower()
    controller.setPower(0.1)
    controller.reverse()

    for500ms(controller.forward)
      .then(() =>
        for500ms(() => {
          controller.reverse()
          controller.forward()
        })
      )
      .then(() => for500ms(controller.stop))
      .then(() => controller.setPower(oldPower))
      .then(resolve())
  })

const for500ms = action =>
  new Promise(resolve =>
    setTimeout(() => {
      action()
      resolve()
    }, 500)
  )
