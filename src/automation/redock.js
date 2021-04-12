import * as controller from '../control'

export default () => {
  const intervalMins = process.env.REDOCK_INTERVAL_MINUTES || 60
  setInterval(() => {
    controller.start(process.argv[2] === 'nopi')
    redock().then(controller.exit)
  }, intervalMins * 1000 * 60)
}

const redock = () =>
  new Promise(resolve => {
    const oldPower = controller.getPower()
    controller.setPower(0.12)
    controller.reverse()

    momentarilyDo(controller.forward)
      .then(() => momentarilyDo(controller.stop)
      .then(() =>
        momentarilyDo(() => {
          controller.reverse()
          controller.forward()
        })
      )
      .then(() =>
        momentarilyDo(() => {
          controller.stop()
          controller.setPower(oldPower)
        })
      )
      .then(resolve)
  })

const momentarilyDo = action =>
  new Promise(resolve =>
    setTimeout(() => {
      action()
      resolve()
    }, 500)
  )
