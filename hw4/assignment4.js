/* hw4 eid fall 18
 *
 * https://www.npmjs.com/package/rpi-dht-sensor
 */

var arrtemperature = [];
var arrhumidity = [];
var cnt = 0;
var sum_temp = 0;
var sum_hmd = 0;
var dht22sensor = require('rpi-dht-sensor');
var dht = new dht22sensor.DHT22(4);
 
function sensorval () 
{
var out = dht.read();
	if(cnt <= 9)
	{
		sum_temp = out.temperature.toFixed(2);
		sum_hmd = out.humidity.toFixed(2);
		arrtemperature.push(sum_temp);
		arrhumidity.push(sum_hmd);
	}
	else
	{
		console.log('Temperature highest at' + Math.max(...arrtemperature) + 'C');
		console.log('Humidity highest at' + Math.max(...arrhumidity) + '%');
		console.log('Temperature lowest at' + Math.min(...arrtemperature) + 'C');
		console.log('Humidity lowest  at' + Math.min(...arrhumidity) + 'C');

	}

setTimeout(sensorval, 10000);

}
sensorval();
