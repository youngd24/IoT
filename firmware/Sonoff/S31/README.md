# S31 Firmware

Factory firmware in here that I backed up from a device

```
esptool.py -b 921600 --port /dev/ttyUSB0 read_flash 0x00000 0x400000 file.bin
```
