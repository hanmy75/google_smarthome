Kodi and Google Home Smarthome action
============================

### Default Config and Update

apt-get update:
```
$ sudo apt-get upgrade
$ sudo apt-get update
```


### KODI

install
```
$ sudo apt-get install kodi
```


### RetroPie

install
```
$ sudo apt-get install git
$ git clone --depth=1 https://github.com/RetroPie/RetroPie-Setup.git
$ cd RetroPie-Setup
$ sudo ./retropie_setup.sh
```
 1. Select Basic install
 2. Manage packages > Manage driver packages > ps3controller

modify bluez daemon (for ps3controller):
```
$ sudo apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
$ git clone https://github.com/luetzel/bluez.git
$ cd ~/bluez
$ ./configure --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --enable-sixaxis
$ make
$ sudo make install
$ sudo service sixad stop
$ sudo systemctl daemon-reload
```

### Pairing with PS3 Controllers:

 1. connect it using an USB cable and wait until it rumbles
 2. run 'sudo sixpair'
 3. disconnect the USB-cable.


Google Home Smarthome action
============================

### Install
```
$ sudo apt-get install python-dev libboost-python-dev python-pip libssl-dev libffi-dev lirc ruby1.9.1 nginx samba samba-common-bin dnsmasq scapy
$ sudo smbpasswd -a pi
```

- WiringPi
```
$ cd ~
$ git clone git://git.drogon.net/wiringPi
$ cd ~/wiringPi/
$ ./build
```

- PI Switch (RF)
```
$ cd ~/wiringPi/
$ sudo pip install pi_switch
```

- lirc
```
$ cd ~
$ git clone https://github.com/loisaidasam/lirc-python
$ cd ~/lirc-python
$ sudo python setup.py install
```

- google_smarthome
```
$ cd ~
$ git clone https://github.com/hanmy75/google_smarthome.git
$ sudo cp ~/google_smarthome/configs/* / -rf
$ sudo chown pi.pi dynudns keys turn_off.sh -R
```

- Install smart home action
```
./gactions update --action_package action.json --project home-auto-b4b9f
```
Reference : https://github.com/actions-on-google/actionssdk-smart-home-nodejs


### Auto login
```
$ sudo systemctl enable autologin@.service
```


### Config

- lirc
```
$ sudo nano /boot/config.txt
-----------------------------------------------------------------
dtoverlay=lirc-rpi,gpio_in_pin=18,gpio_out_pin=27
-----------------------------------------------------------------

$ sudo nano /etc/modules
------------------------------------------------------
lirc_dev
lirc_rpi gpio_in_pin=18 gpio_out_pin=27
------------------------------------------------------

# Copy config file
/etc/lirc/hardware.conf
/etc/lirc/lircd.conf
```
 * You can omit above routine. It is already done before (when you install echo_fauxmo)


### PIN Out
```
RF Switch : GPIO17(GPIO_GEN_0)
IR  : in GPIO18 / out GPIO27
SPEAKER Out : GPIO7
```


### DDNS (https://www.dynu.com)

Config
```
$ cd ~
$ mkdir dynudns
$ cd dynudns
$ nano dynu.sh
------------------------------------------------------
echo url="https://api.dynu.com/nic/update?username=your_id&password=your_password" | curl -k -o ~/dynudns/dynu.log -K -
------------------------------------------------------
$ chmod 755 dynu.sh

$ crontab -e
------------------------------------------------------
10 * * * * /home/pi/dynudns/dynu.sh >/dev/null 2>&1
------------------------------------------------------
```


### SSL Certificate

Install Certbot
```
$ sudo sed -i "$ a\deb http://ftp.debian.org/debian jessie-backports main" /etc/apt/sources.list
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7638D0442B90D010
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8B48AD6246925553
$ sudo apt-get update
$ sudo apt-get install certbot -t jessie-backports -y --force-yes
```

Get SSL Certificate
```
$ sudo certbot certonly
```

Renewal
```
$ crontab -e
------------------------------------------------------
0 */12 * * * root certbot -q renew
------------------------------------------------------
```
