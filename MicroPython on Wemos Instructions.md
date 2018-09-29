## MicroPython on Wemos D1 Instructions

### How to get MicroPython on Wemos with Ubuntu ([source](http://garybake.com/getting-started-with-the-wemos-d1-and-micropython.html))

1. Get last MicroPython firmware for esp8266: https://micropython.org/download/#esp8266  (E.g. esp8266-20180511-v1.9.4.bin)
2. Install esptool for getting firmware image on wemos: 
```
> pip install esptool
```
3. Plug in Wemos to you computer with USB-cable
4. In `/dev/` repository should be something like `ttyUSB0`
5. There are recommedation to erase Wemos first:
```> esptool.py -p /dev/ttyUSB0 erase_flash
esptool.py v1.1
Connecting...
Erasing flash (this may take a while)...
```
Be patien, this take a while.
6. Now flash the wemos with MicroPython:
```
> esptool.py -p /dev/ttyUSB0 write_flash -fm dio -fs 32m -ff 40m 0x00000 /path/to/esp8266-2016-07-28-v1.8.2-58-g3990b17.bin
esptool.py v1.1
Connecting...
Running Cesanta flasher stub...
Flash params set to 0x0240
Writing 512000 @ 0x0... 512000 (100 %)
Wrote 512000 bytes at 0x0 in 44.1 seconds (92.8 kbit/s)...
Leaving...
```
7. Now you can `screen /dev/ttyUSB0 115200` and see python prompt whitch works on microcontroller!
8. Or you can rshell:
```
rshell --buffer-size=30 -p /dev/ttyUSB0 
```
for file exchange or `repl` for python prompt


## How to edit code on Wemos via Wi-Fi

Use page http://micropython.org/webrepl/  where you should insert local IP and Port of your Wemos devise. There are many ways to find out it, for example, look on you router.
