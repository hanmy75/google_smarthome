from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse, json
#from pi_switch import RCSwitchSender
#from lirc import Lirc
import logging


# For TV
TV_MANUFACTORE  = 'Samsung'

# For Light
TABLE_LAMP_OFF_COMMAND         = 0x00EC083B
TABLE_LAMP_ON_COMMAND          = 0x00EC083C
LIVINGROOM_LAMP_OFF_COMMAND    = 0x00EB083D
LIVINGROOM_LAMP_ON_COMMAND     = 0x00EB083C
WINDOW_LAMP_OFF_COMMAND        = 0x00EA083E
WINDOW_LAMP_ON_COMMAND         = 0x00EA083F
GROUP_ON_COMMAND               = 0xABCDEF00
GROUP_OFF_COMMAND              = 0xABCDEF11


# RCU Operation
def RCU_Operation(key_code):
    logging.debug("RCU : code %s", key_code)
    #lirc_obj.send_once(TV_MANUFACTORE, key_code)

# RF Operation
def RF_Operation(key_code):
    logging.debug("RF : code %s", key_code)
    #rf_sender.sendDecimal(key_code, 24)

# Power On Off Control
def do_PowerOnOff(device, onoff):
	operation = device['operation']
	if onoff == 'true':
		operation['function'](operation['on_key'])
	else:
		operation['function'](operation['off_key'])
	# Update Status
	device['status'] = onoff


############################
## Define device property
############################
devicePropertys = [
	{
		'id': '1',
		'type': 'action.devices.types.SWITCH',
		'traits': [
		    'action.devices.traits.OnOff',
		],
		'name': {
		    'name': 'TV'
		},
		'operation': {
			'function' : RCU_Operation,
			'on_key' : 'KEY_POWER',
			'off_key': 'KEY_POWER'
		},
		'status' : 'false'
	},
	{
		'id': '2',
		'type': 'action.devices.types.LIGHT',
		'traits': [
		    'action.devices.traits.OnOff',
		],
		'name': {
		    'name': 'Table'
		},
		'operation': {
			'function': RF_Operation,
			'on_key': TABLE_LAMP_ON_COMMAND,
			'off_key': TABLE_LAMP_OFF_COMMAND
		},
		'status': 'false'
	},
	{
		'id': '3',
		'type': 'action.devices.types.LIGHT',
		'traits': [
			'action.devices.traits.OnOff',
		],
		'name': {
			'name': 'Center'
		},
		'operation': {
			'function': RF_Operation,
			'on_key': LIVINGROOM_LAMP_ON_COMMAND,
			'off_key': LIVINGROOM_LAMP_OFF_COMMAND
		},
		'status': 'false'
	},
	{
		'id': '4',
		'type': 'action.devices.types.LIGHT',
		'traits': [
			'action.devices.traits.OnOff',
		],
		'name': {
			'name': 'Window'
		},
		'operation': {
			'function': RF_Operation,
			'on_key': WINDOW_LAMP_ON_COMMAND,
			'off_key': WINDOW_LAMP_OFF_COMMAND
		},
		'status': 'false'
	}
]



class GetHandler(BaseHTTPRequestHandler):

	def do_POST(self):
		content_len = int(self.headers.getheader('content-length'))
		post_body = self.rfile.read(content_len)
		data = json.loads(post_body)
		response_result = {}

		logging.info("POST path : %s", self.path)
		logging.info("POST data : %s", data)

		# Check URL
		if self.path != '/smarthome':
			self.send_response(401, "invalid URL")
			self.end_headers()
			return

		# Check Input Data
		found_flag = False
		for one_data in data:
			if one_data == 'inputs':
				found_flag = True
				break
		if found_flag == False:
			self.send_response(401, "missing intent")
			self.end_headers()
			return

		for one_input in data['inputs']:
			don_flag = False
			if one_input['intent'] == 'action.devices.SYNC':
				response_result = self.do_sync(data['requestId'])
				don_flag = True
			elif one_input['intent'] == 'action.devices.QUERY':
				response_result = self.do_query(data['requestId'], one_input['payload']['devices'])
				don_flag = True
			elif one_input['intent'] == 'action.devices.EXECUTE':
				response_result = self.do_execute(data['requestId'], one_input['payload']['commands'])
				don_flag = True
			else:
				self.send_response(401, "missing intent")
				self.end_headers()

			if don_flag == True:
				self.send_response(200)
				self.end_headers()
				self.wfile.write(json.dumps(response_result))
				logging.info("POST response : %s", json.dumps(response_result))
		return

	# SYNC
	def do_sync(self, requestId):
		deviceProperty = []
		respProps = {
			'requestId': requestId,
			'payload': {
				'devices': deviceProperty
			}
		}

		# Update Device Property Information
		for one_property in devicePropertys:
			logging.debug("SYNC : id %s, name %s", one_property['id'], one_property['name'])
			deviceProperty.append({'id': one_property['id'],  'type': one_property['type'], 'traits': one_property['traits'], 'name': one_property['name'], 'willReportState': 'true'})

		return respProps

	# QUERY
	def do_query(self, requestId, inDevicesInfo):
		respStatus = {}
		deviceStates = {
			'requestId': requestId,
			'payload': {
				'devices': respStatus
			}
		}

		logging.info("QUERY : %s", inDevicesInfo)

		for one_device_info in inDevicesInfo:
			# Find matched device ID
			for one_device in devicePropertys:
				if one_device['id'] == one_device_info['id']:
					logging.debug("QUERY : device %s, status %s", one_device['id'], one_device['status'])
					respStatus.update({one_device['id']: {'on': one_device['status'], 'online': 'true'}})

		return deviceStates

	# EXECUTE
	def do_execute(self, requestId, commands):
		respCommands = []
		responseBody = {
			'requestId': requestId,
			'payload': {
				'commands': respCommands
			}
		}

		logging.info("EXECUTE : %s", commands)

		for one_command in commands:
			for one_device_info in one_command['devices']:
				for one_execution in one_command['execution']:
					logging.debug("QUERY : device %s, execution %s", one_device_info['id'], one_execution['command'])

					# Find matched device ID
					for one_device in devicePropertys:
						if one_device['id'] == one_device_info['id']:
							# Power On Off Command
							if one_execution['command'] == 'action.devices.commands.OnOff':
								do_PowerOnOff(one_device, one_execution['params']['on'])

						respCommands.append({'ids': [one_device['id']], 'status': "SUCCESS"})

		return responseBody




# Lirc Init
#lirc_obj = Lirc()

# RF Switch Init
#rf_sender = RCSwitchSender()
#rf_sender.enableTransmit(0)  # GPIO_GEN_0

# Setup logging level
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
	from BaseHTTPServer import HTTPServer
	server = HTTPServer(('localhost', 4003), GetHandler)
	print 'Starting server at http://localhost:4003'
	server.serve_forever()
