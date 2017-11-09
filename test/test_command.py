import requests
# POST with JSON
import json

URL = "http://192.168.0.10:4003/smarthome"
headers = {'authorization': 'Bearer psokmCxKjfhk7qHLeYd1'}

# Example for EXECUTE
exec_payload = {'commands':[{'devices':[{'id':'2'}],'execution':[{'command':'action.devices.commands.OnOff','params':{'on':'true'}}]}]}
#data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.EXECUTE', 'payload': exec_payload}]}

# Example for SYNC
#data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.SYNC'}]}

# Example for QUERY
query_payload = {'devices': {'1': {'on': 'true', 'online': 'true'}, '2': {'on': 'true', 'online': 'true'}, '3': {'on': 'true', 'online': 'true'}, '4': {'on': 'true', 'online': 'true'}}}
data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.QUERY', 'payload': query_payload}]}


requests.post(URL, headers=headers, json=data)
