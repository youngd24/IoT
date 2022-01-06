## Installing MicroPython on a Wemos S2 Mini

* Original instructions are [here](https://www.wemos.cc/en/latest/tutorials/s2/get_started_with_micropython_s2.html)
* Board specs are [here](https://www.wemos.cc/en/latest/s2/s2_mini.html)


## Requirements

* Python
* esptool (for flash esp32-s2 firmware.)

```
pip install esptool
```

## S2 MINI Firmware
* [s2_mini_micropython_v1.16-200-g1b87e1793.bin](https://www.wemos.cc/en/latest/_static/files/s2_mini_firmware/s2_mini_micropython_v1.16-200-g1b87e1793.bin)

## Flash firmware

Make S2 boards into Device Firmware Upgrade (DFU) mode.

* Hold on Button 0
* Press Button Reset
* Release Button 0 When you hear the prompt tone on usb reconnection

Flash using esptool.py

```
esptool.py --port PORT_NAME erase_flash
esptool.py --port PORT_NAME --baud 1000000 write_flash -z 0x1000 FIRMWARE.bin
```
