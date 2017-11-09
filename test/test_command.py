import requests
# POST with JSON 
import json

URL = "http://192.168.0.10:4003/smarthome"
headers = {'authorization': 'Bearer psokmCxKjfhk7qHLeYd1'}

# Example for EXECUTE
payload = {'commands':[{'devices':[{'id':'2'}],'execution':[{'command':'action.devices.commands.OnOff','params':{'on':'true'}}]}]}
data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.EXECUTE', 'payload': payload}]}

# Example for SYNC
#data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.SYNC'}]}


requests.post(URL, headers=headers, json=data)
