Google Smarthome Action
============================

### Setup Instructions

Reference : https://github.com/actions-on-google/actionssdk-smart-home-nodejs

1. Install node and 
```
wget https://nodejs.org/dist/v6.9.5/node-v6.9.5-linux-armv6l.tar.xz
tar -xvf node-v6.9.5-linux-armv6l.tar.xz
cd node-v6.9.5-linux-armv6l
sudo cp -R * /usr/local/
```

2. Register Action
```
./gactions update --action_package action.json --project home-auto-b4b9f
```

3. Install smart-home-cloud.js
```
cd server
npm install
```

4. Run smart-home-cloud.js
```
node smart-home-cloud.js
```
