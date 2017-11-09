import requests
# POST with JSON 
import json

headers = {'authorization': 'Bearer psokmCxKjfhk7qHLeYd1'}

payload = {'commands':[{'devices':[{'id':'2'}],'execution':[{'command':'action.devices.commands.OnOff','params':{'on':'true'}}]}]}
#contents = {"uid":"1234","auth":"psokmCxKjfhk7qHLeYd1","requestId":"6433088915707706447", 'payload': payload}
data = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.EXECUTE'}, {'payload': payload}]}

#payload = {'requestId': 'ff36a3cc-ec34-11e6-b1a0-64510650abcf', 'inputs': [{'intent': 'action.devices.SYNC'}]}

requests.post("http://192.168.0.10:4003/smarthome", headers=headers, json=data)
