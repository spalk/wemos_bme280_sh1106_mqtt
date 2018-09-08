import machine, time, sh1106, bme280, ntptime
from umqtt.simple import MQTTClient

pinScl      = 5   # ESP8266 GPIO5 (D1)
pinSda      = 4   # ESP8266 GPIO4 (D2)
addrOled    = 60  # 0x3c
addrBME280  = 118 # 0x76
hSize       = 64  # display heigh in pixels
wSize       = 128 # display width in pixels

temp = 0          # temperature from BME280
pres = 0          # atmospheric pressure from BME280
humi = 0          # humidity from BME280

temp_out = 0      # outside temperature via mqtt


# init ic2 object
i2c = machine.I2C(scl=machine.Pin(pinScl), sda=machine.Pin(pinSda)) 

# mqtt messaged frequency
msg_frq = 60  # every 1 minute
now_mqtt = time.time()

# init display
display = sh1106.SH1106_I2C(128, 64, i2c, machine.Pin(16), 0x3c)

# time synchroninize freq
ntptime.settime()
time_synq_frq = 86400  # everyday
now_time = time.time()


while True:
  # get bme280 sensor data
  bme = bme280.BME280(i2c=i2c,address=addrBME280)
  bme_data = bme.read_compensated_data()
  temp = bme_data[0]/100              # degrees Celsius
  pres = bme_data[1]/256/100000*750   # mm Hg 
  humi = bme_data[2]/1024             # relative humidity

  # current time
  hour = str(time.localtime(time.time()+10800)[3])   #  10800 seq == +3 hours - Moscow time
  minute = str(time.localtime(time.time()+10800)[4])
  if len(str(hour)) == 1:
    hour = '0' + hour
  if len(str(minute)) == 1:
    minute = '0' + minute

  # show info on display
  display.sleep(False)
  display.contrast(0)
  display.fill(0)
  display.text('* %s:%s *' % (hour, minute), 30, 0, 1)
  display.line(0,10,128,10,1)
  display.text('T.ins = '+'{:.1f}'.format(temp)+' C', 0, 20, 1)
  display.text('Humid = '+'{:.0f}'.format(humi)+' %', 0, 30, 1)
  display.text('Press = '+'{:.0f}'.format(pres)+'mmHg', 0, 40, 1)
  display.text('T.out = xx.x C', 0, 50, 1)
  display.show()

  # send mqtt messages to brocker
  if time.time() - now_mqtt > msg_frq:
    client = MQTTClient('wemos-d1-mini-001', server='io.adafruit.com', user='Spalk', password='dfdd23126c5a4cd68ef8404e0f7c6b06')
    client.connect()
    client.publish('Spalk/feeds/kidsroom.temp', str(temp))
    client.publish('Spalk/feeds/kidsroom.humid', str(humi))
    client.publish('Spalk/feeds/weather.pressure', str(pres))
    now_mqtt = time.time()

  # time sync
  if time.time() - now_time > time_synq_frq:
    ntptime.settime()

  time.sleep_ms(5000)
