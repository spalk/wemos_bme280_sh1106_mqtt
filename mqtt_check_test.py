import time
from umqtt.simple import MQTTClient


# mqtt subscribe
def sub_cb(topic, msg):
  print((topic, msg))


client = MQTTClient('thinkpad_test_001', server='io.adafruit.com', user='Spalk', password='dfdd23126c5a4cd68ef8404e0f7c6b06')
client.set_callback(sub_cb)
client.connect()
client.subscribe(topic="Spalk/feeds/weather.temp") 

b = False

while True:
    if b:
        print('waiting..')
        client.wait_msg()
    else:
        client.check_msg()
        print('check..')
        #client.disconnect()
        time.sleep(1)
client.disconnect()