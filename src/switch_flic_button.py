import time
import random
import string
import logging
import requests
import fliclib

# POST with JSON
import json

DEBOUNCE_SECONDS = 3

URL = "http://localhost:4003/smarthome"
DEVICE_ADDR = "80:e4:da:72:7b:e8"

devicePropertys = []
lightIDs = []
lastTriggerTime = 0


# Setup logging level
logging.basicConfig(level=logging.DEBUG)

client = fliclib.FlicClient("localhost")

# For requestId
def getRandonString():
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

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
    data = json.loads(resp.text)
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
    data = json.loads(resp.text)

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


# Debounce triggering
def debounce():
    global lastTriggerTime
    debounceFlag = False

    if (time.time() - lastTriggerTime) < DEBOUNCE_SECONDS:
        debounceFlag = True

    lastTriggerTime = time.time()
    return debounceFlag

# Process Light
def process_light():
    if debounce():
        logging.debug("Trigger debounced.")
        return

    lightFlag = isAnyLightOn()
    logging.debug("Light is %d", lightFlag)
    # Toggle Light
    if lightFlag == 1:
        turnOnOffLight(False)
    else:
        turnOnOffLight(True)

# Button detect event
def got_button(channel, click_type, was_queued, time_diff):
    if (channel.bd_addr == DEVICE_ADDR and str(click_type) == "ClickType.ButtonDown") :
        logging.debug("Button pressed.")
        process_light()

def got_info(items):
    print(items)
    for bd_addr in items["bd_addr_of_verified_buttons"]:
        cc = fliclib.ButtonConnectionChannel(bd_addr)
        cc.on_button_up_or_down = got_button
        client.add_connection_channel(cc)


# Main routine
devicePropertys = getDevicePropertys()

# Register Flic info
client.get_info(got_info)
client.handle_events()
