# Intro


# Flash Operations

## Get Info

To get the flash_id:

```
esptool.py --port /dev/ttyUSB0 --baud 921600 flash_id
```

To get the chip_id

```
esptool.py --port /dev/ttyUSB0 --baud 921600 chip_id
```

## Erase

To erase flash:

```
esptool.py --port /dev/ttyUSB0 --baud 921600 erase_flash
```


# Reference Material

https://github.com/nodemcu/nodemcu-firmware
http://www.nodemcu.com/index_en.html
