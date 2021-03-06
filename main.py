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
#display_show('I2C Init...')
i2c = machine.I2C(scl=machine.Pin(pinScl), sda=machine.Pin(pinSda)) 
#display_show('OK')

# init display
display = sh1106.SH1106_I2C(128, 64, i2c, machine.Pin(16), 0x3c)
display_switch = 'ON'

def display_show(message):
  display.fill(0)
  display.text(str(message), 0, 20, 1)
  display.show()
  time.sleep_ms(1000)

display_show('HELLO! =)')

# mqtt messaged frequency
msg_frq = 60  # every 1 minute
now_mqtt = time.time()

# mqtt init and subscribe
def sub_cb(topic, msg):
  global temp_out
  global display_switch
  print('Recieved from brocker: ', (topic, msg))
  if topic.decode('utf-8') == 'house/outside/temp':
    temp_out = msg.decode('utf-8')
  elif topic.decode('utf-8') == 'house/kidsroom/oled':
    display_switch = msg.decode('utf-8')
  else:
    pass

# get brocker account info from config
brkf = open('brocker.conf').readlines()
brocker = {}
brocker['server']   = brkf[0].replace('\n','')
brocker['user']     = brkf[1].replace('\n','')
brocker['password'] = brkf[2].replace('\n','')

display_show('Brocker conn...')
client = MQTTClient('wemos-d1-mini-001', server=brocker['server'], user=brocker['user'], password=brocker['password'])
client.set_callback(sub_cb)
client.connect()
client.subscribe(topic='house/outside/temp') 
client.subscribe(topic='house/kidsroom/oled') 
display_show('OK')


# time synchroninize freq
#display_show('Getting time...')
#print('Get time from ntp server...')
ntptime.settime()
time_synq_frq = 3600  # every hour
now_time = time.time()
#display_show('OK')

 # get bme280 sensor data
#display_show('BME i2c init...')
bme = bme280.BME280(i2c=i2c,address=addrBME280)
#display_show('OK')

while True:

  try:
    #display_show('Read BME data...')
    bme_data = bme.read_compensated_data()
    temp = bme_data[0]/100              # degrees Celsius
    pres = bme_data[1]/256/100000*750   # mm Hg 
    humi = bme_data[2]/1024             # relative humidity
    #display_show('OK')
  except:
    display_show('Failed')
    client.publish('system/log/error', 'BME')


  # check new mqtt messages
  try:
    #display_show('Check brkr msgs...')
    client.check_msg()
    #display_show('OK')
  except:
    display_show('Failed')
    client.publish('system/log/error', 'check brocker messages')


  # recive and send mqtt messages to brocker
  if time.time() - now_mqtt > msg_frq:
    try:
      #display_show('Send data to brk')
      print('Sending temp, humid, press to brocker...', temp, humi, pres)
      client.publish('house/kidsroom/temp', str(temp))
      client.publish('house/kidsroom/humid', str(humi))
      client.publish('house/outside/pressure', str(pres))
      now_mqtt = time.time()
      display_show('OK')
    except:
      display_show('Failed')
      client.publish('system/log/error', 'Publishing data')

  # current time
  hour = str(time.localtime(time.time()+10800)[3])   #  10800 seq == +3 hours - Moscow time
  minute = str(time.localtime(time.time()+10800)[4])
  if len(str(hour)) == 1:
    hour = '0' + hour
  if len(str(minute)) == 1:
    minute = '0' + minute

  # show info on display
  if display_switch == 'ON':
    display.sleep(False)
    display.contrast(0)
    display.fill(0)
    display.text('* %s:%s *' % (hour, minute), 30, 0, 1)
    display.line(0,10,128,10,1)
    display.text('T.ins = '+'{:.1f}'.format(temp)+' C', 0, 20, 1)
    display.text('Humid = '+'{:.0f}'.format(humi)+' %', 0, 30, 1)
    display.text('Press = '+'{:.0f}'.format(pres)+'mmHg', 0, 40, 1)
    if temp_out:
      display.text('T.out = '+temp_out+' C', 0, 50, 1)
    display.show()
  else:
    display.fill(0)
    display.show()

  # time sync
  if time.time() - now_time > time_synq_frq:
    print('Time synq...')
    try:
      display_show('Time synq...')
      ntptime.settime()
      now_time = time.time()
      print('Successful')
  #    display_show('OK')
    except:
      display_show('Failed')
      print('Unsuccessful')
      client.publish('system/log/error', 'Tyme sync error')

  time.sleep_ms(10000)

client.disconnect()
