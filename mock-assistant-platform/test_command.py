import requests
# POST with JSON
import json

URL = "http://339a6f04.ngrok.io/smarthome"
headers = {'authorization': 'Bearer psokmCxKjfhk7qHLeYd1'}

# Example for EXECUTE
exec_payload = {'commands':[{'devices':[{'id':'1'}],'execution':[{'command':'action.devices.commands.OnOff','params':{'on':'true'}}]}]}
exec_data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.EXECUTE', 'payload': exec_payload}]}

# Example for SYNC
sync_data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.SYNC'}]}

# Example for QUERY
query_payload = {'devices': [{'id': '1'}, {'id': '2'}, {'id': '3'}, {'id':'4'}]}
query_data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.QUERY', 'payload': query_payload}]}


requests.post(URL, headers=headers, json=sync_data)

requests.post(URL, headers=headers, json=exec_data)

requests.post(URL, headers=headers, json=query_data)

