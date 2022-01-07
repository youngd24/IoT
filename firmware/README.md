# Firmware

Most of what's in here is for Espressif ESP devices as that's what I generally use.

## For 1M Flash

### Backup Firmware

```
esptool.py -b 921600 --port /dev/ttyUSB0 read_flash 0x000000 0x100000 flash_1M.bin
```

### Write Firmware

```
esptool.py -b 921600 --port /dev/ttyUSB0 write_flash 0x000000 flash_1M.bin
```

### For 4M Flash

### Backup Firmware

```
esptool.py -b 921600 --port /dev/ttyUSB0 read_flash 0x00000 0x400000 flash_4M.bin
```

### Write Firmware

```
esptool.py -b 921600 --port /dev/ttyUSB0 write_flash 0x000000 flash_4M.bin
```
