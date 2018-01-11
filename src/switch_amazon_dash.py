import random
import string
import logging
import requests
# POST with JSON
import json
from scapy.all import *

URL = "http://localhost:4003/smarthome"
MAC_ADDRESS = 'fc:a6:67:20:7c:99' # enter Dash Button's MAC Address here.

devicePropertys = []
lightIDs = []

# Setup logging level
logging.basicConfig(level=logging.DEBUG)

# For requestId
def getRandonString():
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

# Device Property
def getDevicePropertys():
    local_deviceProperty = []
    # SYNC Data format
    req_data = {
        'requestId': getRandonString(),
        'inputs': [
            {'intent': 'action.devices.SYNC'}
        ]
    }

    resp = requests.post(URL, headers='', json=req_data)
    data = json.loads(resp.content)
    input_data = data.get('payload')
    if input_data != None:
        local_deviceProperty = input_data['devices']
        # Search LIGHT type on Device Property
        for one_device in local_deviceProperty:
            if one_device['type'] == 'action.devices.types.LIGHT':
                logging.debug("Find LIGHT ID : %s", one_device['id'])
                lightIDs.append(one_device['id'])

    return local_deviceProperty


# Device Status : Only for LIGHT
def isAnyLightOn():
    lightFlag = False
    payload = {'devices': []}
    # QUERY Data format
    req_data = {
        'requestId': getRandonString(),
        'inputs': [
            {'intent': 'action.devices.QUERY',
             'payload': payload
             }
        ]
    }

    # Search LIGHT type on Device Property
    for id in lightIDs:
        logging.debug("Add LIGHT ID : %s", id)
        payload['devices'].append({'id': id})

    # Request QUERY
    resp = requests.post(URL, headers='', json=req_data)
    data = json.loads(resp.content)

    # Get LIGHT status
    input_data = data.get('payload')
    if input_data != None:
        for one_id in lightIDs:
            one_status = input_data['devices'].get(str(one_id))
            logging.debug("ID(%d) : %s ", one_id, one_status)
            if one_status['on'] == True:
                lightFlag = True

    return lightFlag

# Trun On/Off Light
def turnOnOffLight(onoff):
    payload = {'commands':[
                    {'devices': [],
                            'execution': [
                                {'command': 'action.devices.commands.OnOff',
                                 'params': {'on': onoff}
                                 }
                            ]
                }]
    }
    # EXECUTE Data format
    req_data = {
        'requestId': getRandonString(),
        'inputs': [
            {'intent': 'action.devices.EXECUTE',
             'payload': payload
             }
        ]
    }

    # Add IDs
    devices = payload['commands'][0].get('devices')
    if devices != None:
        for one_id in lightIDs:
            devices.append({'id': str(one_id)})

    # Request EXECUTE
    requests.post(URL, headers='', json=req_data)

# Detect dash button
def detect_button(pkt):
    if pkt.haslayer(DHCP) and pkt[Ether].src == MAC_ADDRESS:
            logging.debug("Button Press Detected")
            lightFlag = isAnyLightOn()
            logging.debug("Light is %d", lightFlag)
            # Toggle Light
            if lightFlag == 1:
                turnOnOffLight(False)
            else:
                turnOnOffLight(True)


# Main routine
devicePropertys = getDevicePropertys()

# Loop to detect dash button
sniff(prn=detect_button, filter="(udp and (port 67 or 68))", store=0)
