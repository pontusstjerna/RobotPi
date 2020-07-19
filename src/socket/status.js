import { exec } from 'child_process'
import { isCharging } from '../control'

export default socket => {
  socket.on('status', () => {
    exec('./get_status.sh', (err, stdout, stderr) => {
      if (err) {
        socket.emit('status', null)
        console.log(err)
        return
      }

      isCharging().then(isCharging => {
        const status = {
            ...parseStatus(stdout),
            isCharging
        }
  
        socket.emit('status', JSON.stringify(status))
      })
    })
  })
}

const parseStatus = bufferedString => {
  const split = bufferedString.split('\n').splice(0, 6)

  const statusValues = split.map(row => parseStatusRow(row))

  if (statusValues.length !== 6) {
    return null
  }

  return {
    throttled: parseThrottledBitStatus(statusValues[0]),
    temp: statusValues[1],
    volts: {
      core: statusValues[2],
      sdram_c: statusValues[3],
      sdram_i: statusValues[4],
      sdram_p: statusValues[5],
    },
  }
}

const parseStatusRow = row => {
  if (row) {
    const splitRow = row.split('=')
    if (splitRow.length === 2) {
      return splitRow[1]
    }
  }
  return null
}

const parseThrottledBitStatus = bitStatus => {
  const bits = parseInt(bitStatus).toString(2)
  let status = ''

  if (bits[0] === '1') {
    status += 'Under-voltage detected. '
  }

  if (bits[1] === '1') {
    status += 'Arm frequency capped. '
  }

  if (bits[2] === '1') {
    status += 'Currently throttled (slowed CPU). '
  }

  if (bits[3] === '1') {
    status += 'Soft temperature limit active. '
  }

  if (bits[16] === '1') {
    status += 'Under-voltage has occurred. '
  }

  if (bits[17] === '1') {
    status += 'Arm frequency capped has occurred. '
  }

  if (bits[18] === '1') {
    status += 'Throttling has occurred. '
  }

  if (bits[19] === '1') {
    status += 'Soft temperature limit has occurred.'
  }

  return status
}
