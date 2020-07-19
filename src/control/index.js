import PythonShell from 'python-shell'

const OPEN = 'open'
const CLOSED = 'closed'

let shell

export let power = 1

export const forward = () => {
  setMotorLeft(power)
  setMotorRight(power)
}

export const left = () => {
  setMotorLeft(power)
  setMotorRight(power * 0.1)
}

export const right = () => {
  setMotorLeft(power * 0.1)
  setMotorRight(power)
}

export const rotLeft = () => {
  setMotorLeft(power * 0.8)
  setMotorRight(-power * 0.8)
}

export const rotRight = () => {
  setMotorLeft(-power * 0.8)
  setMotorRight(power * 0.8)
}

export const reverse = () => {
  power = -power
}

export const stop = () => {
  setMotorLeft(0)
  setMotorRight(0)
}

export const startCharging = () => setMOSFET(OPEN)

export const stopCharging = () => setMOSFET(CLOSED)

export const start = debug => {
  if (!debug) {
    shell = new PythonShell('python/controller.py')
  } else {
    shell = new PythonShell('python/test.py')
  }

  shell.on('message', message => {
    console.log('py: ' + message)
  })
}

export const exit = () => {
  shell.send('quit')
  shell.end((err, code, signal) => {
    if (err) throw err
    console.log('Python exited with code ' + code)
  })
}

const setMotorRight = pwr => {
  shell.send('HBridge.setMotorRight(' + pwr + ')')
  console.log('')
}

const setMotorLeft = pwr => {
  shell.send('HBridge.setMotorLeft(' + pwr + ')')
  console.log('')
}

const setMOSFET = state => {
  shell.send(`MOSFETBridge.setState(${state})`)
  console.log('')
}
