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


############################
## Define device property
############################
deviceProperty = {
	'devices': [
	{
		'id': '1',
		'type': 'action.devices.types.LIGHT',
		'traits': [
		    'action.devices.traits.OnOff',
		],
		'name': {
		    'name': 'Window'
		},
		'willReportState': 'true'
	},
	{
		'id': '2',
		'type': 'action.devices.types.LIGHT',
		'traits': [
		    'action.devices.traits.OnOff',
		],
		'name': {
		    'name': 'Center'
		},
		'willReportState': 'true'
	},
	{
		'id': '3',
		'type': 'action.devices.types.LIGHT',
		'traits': [
		    'action.devices.traits.OnOff',
		],
		'name': {
		    'name': 'Table'
		},
		'willReportState': 'true'
	},
	{
		'id': '4',
		'type': 'action.devices.types.SWITCH',
		'traits': [
		    'action.devices.traits.OnOff',
		],
		'name': {
		    'name': 'TV'
		},
		'willReportState': 'true'
	}
	]
}


# RCU Operation
def RCU_Operation(key_code):
    logging.debug("RCU : code %s", key_code)
    #lirc_obj.send_once(TV_MANUFACTORE, key_code)

# RF Operation
def RF_Operation(key_code):
    logging.debug("RF : code %s", key_code)
    #rf_sender.sendDecimal(key_code, 24)


# [0] : Device ID
# [1] : Device Name
# [2] : Function
# [3] : On key
# [4] : Off key
# [5] : Status
DEVICE_LIST = [
    ['1', "TV", RCU_Operation, 'KEY_POWER', 'KEY_POWER', 'false'],
    ['2', "table", RF_Operation, TABLE_LAMP_ON_COMMAND, TABLE_LAMP_OFF_COMMAND, 'false'],
    ['3', "center", RF_Operation, LIVINGROOM_LAMP_ON_COMMAND, LIVINGROOM_LAMP_OFF_COMMAND, 'false'],
    ['4', "window", RF_Operation, WINDOW_LAMP_ON_COMMAND, WINDOW_LAMP_OFF_COMMAND, 'false']
]

# Power On Off Control
def do_PowerOnOff(id, onoff):
    for one_device in DEVICE_LIST:
		if one_device[0] == id:
			if onoff == 'true':
				one_device[2](one_device[3])
			else:
				one_device[2](one_device[4])
			# Update Status
			one_device[5] = onoff

# Get Device Status
def get_PowerStatus(id):
	onoff_status = 'false'
	for one_device in DEVICE_LIST:
		if one_device[0] == id:
			onoff_status = one_device[5]
	return onoff_status



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
		deviceProps = {
			'requestId': requestId,
			'payload': deviceProperty
		}

		return deviceProps

	# QUERY
	def do_query(self, requestId, devices):
		respStatus = {}
		deviceStates = {
			'requestId': requestId,
			'payload': {
				'devices': respStatus
			}
		}

		logging.info("QUERY : %s", devices)

		for one_device in devices:
			logging.debug("QUERY : device %s, status %s", one_device['id'], get_PowerStatus(one_device['id']))
			respStatus.update({one_device['id']: {'on': get_PowerStatus(one_device['id']), 'online': 'true'}})

		return deviceStates

	# EXECUTE
	def do_execute(self, requestId, commands):
		respCommands = {}
		responseBody = {
			'requestId': requestId,
			'payload': {
				'commands': respCommands
			}
		}

		logging.info("EXECUTE : %s", commands)

		for one_command in commands:
			for one_device in one_command['devices']:
				for one_execution in one_command['execution']:
					logging.debug("QUERY : device %s, execution %s", one_device['id'], one_execution['command'])

					# Power On Off Command
					if one_execution['command'] == 'action.devices.commands.OnOff':
						do_PowerOnOff(one_device['id'], one_execution['params']['on'])


					respCommands.update({'ids': [one_device['id']], 'status': "SUCCESS"})

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
