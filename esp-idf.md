## Install esp-idf

### Linux

This was my setup on my Lab Pi 4. YMMV, sources included

* ESP-IDF installation docs [here](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html)
* Someone else has Ansible for [this](https://github.com/tchisaka/Ansible/blob/master/TinkerOS/Arduino-ESP32.sh). It's dated but seems like it would work. Another one is [here](https://github.com/wolfeidau/ansible-esp8266-role).

####Install pre-requisites

```
sudo apt-get install git wget flex bison gperf python3 python3-pip python3-setuptools cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0
```

#### Install ESP-IDF Tools (standalone)

* Installation instructions [here](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html#get-started-get-esp-idf)
* Installs into `$HOME/Apps/esp-idf`

#### Clone & Setup
* Clone their repo (this takes a while)

```
mkdir -p ~/Apps/esp-idf
cd ~/Apps/esp-idf
git clone --recursive https://github.com/espressif/esp-idf.git
```

* Set up the environment
* Possible chip targets are: esp32, esp32c3, esp32s2, esp32s3 or "all".

```
cd ~/Apps/esp-idf
./install.sh esp32
```
