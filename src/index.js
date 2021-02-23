import connectMqtt from './mqtt'

const started = connectMqtt()
console.log(`Cat Hunter started at ${started}`)
