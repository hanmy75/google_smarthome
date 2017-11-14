import urlparse, json, requests
import threading
import fauxmo
import time
import logging
from BaseHTTPServer	import BaseHTTPRequestHandler
from pi_switch import RCSwitchSender
from lirc import Lirc

# For request sync to Google Home : 30 min
REQUEST_SYNC_DURATION = (30*60)
AGENT_USER_ID = 'han.my75@gmail.com'
API_KEY = 'AIzaSyBHnS2UwDuHfQd6HX6ce5WoDFB4ZT0Hhe8'
requestSyncHeaders = {'Content-Type': 'application/json'}
requestSyncEndpoint = 'https://homegraph.googleapis.com/v1/devices:requestSync?key='


# Lirc Init
lirc_obj = Lirc()

# RF Switch	Init
rf_sender =	RCSwitchSender()
rf_sender.enableTransmit(0)	 # GPIO_GEN_0

# Setup	logging	level
logging.basicConfig(level=logging.DEBUG)


# RCU Operation
def	RCU_Operation(key_code):
	logging.debug("RCU : code %s", key_code)
	lirc_obj.send_once(TV_MANUFACTORE, key_code)

# RF Operation
def	RF_Operation(key_code):
	logging.debug("RF :	code %s", key_code)
	rf_sender.sendDecimal(key_code,	24)

# Power	On Off Control
def	do_PowerOnOff(device, onoff):
	operation =	device['operation']
	if onoff ==	True:
		operation['function'](operation['on_key'])
	else:
		operation['function'](operation['off_key'])
	# Update Status
	device['status'] = onoff
	time.sleep(0.1)


# For TV
TV_MANUFACTORE	= 'Samsung'

# For Light
TABLE_LAMP_OFF_COMMAND		   = 0x00EC083B
TABLE_LAMP_ON_COMMAND		   = 0x00EC083C
LIVINGROOM_LAMP_OFF_COMMAND	   = 0x00EB083D
LIVINGROOM_LAMP_ON_COMMAND	   = 0x00EB083C
WINDOW_LAMP_OFF_COMMAND		   = 0x00EA083E
WINDOW_LAMP_ON_COMMAND		   = 0x00EA083F
GROUP_ON_COMMAND			   = 0xABCDEF00
GROUP_OFF_COMMAND			   = 0xABCDEF11


############################
## Define device property
############################
devicePropertys	= [
	{
		'id': 1,
		'type':	'action.devices.types.SWITCH',
		'traits': [
			'action.devices.traits.OnOff',
		],
		'name':	{
			'name':	'TV'
		},
		'operation': {
			'function' : RCU_Operation,
			'on_key' : 'KEY_POWER',
			'off_key': 'KEY_POWER'
		},
		'status' : False
	},
	{
		'id': 2,
		'type':	'action.devices.types.LIGHT',
		'traits': [
			'action.devices.traits.OnOff',
		],
		'name':	{
			'name':	'Table'
		},
		'operation': {
			'function':	RF_Operation,
			'on_key': TABLE_LAMP_ON_COMMAND,
			'off_key': TABLE_LAMP_OFF_COMMAND
		},
		'status': False
	},
	{
		'id': 3,
		'type':	'action.devices.types.LIGHT',
		'traits': [
			'action.devices.traits.OnOff',
		],
		'name':	{
			'name':	'Center'
		},
		'operation': {
			'function':	RF_Operation,
			'on_key': LIVINGROOM_LAMP_ON_COMMAND,
			'off_key': LIVINGROOM_LAMP_OFF_COMMAND
		},
		'status': False
	},
	{
		'id': 4,
		'type':	'action.devices.types.LIGHT',
		'traits': [
			'action.devices.traits.OnOff',
		],
		'name':	{
			'name':	'Window'
		},
		'operation': {
			'function':	RF_Operation,
			'on_key': WINDOW_LAMP_ON_COMMAND,
			'off_key': WINDOW_LAMP_OFF_COMMAND
		},
		'status': False
	}
]


# Google Smart Home	action Main	Handler
class GetHandler(BaseHTTPRequestHandler):

	def	do_POST(self):
		content_len	= int(self.headers.getheader('content-length'))
		post_body =	self.rfile.read(content_len)
		data = json.loads(post_body)
		response_result	= {}

		logging.info("POST path : %s", self.path)
		logging.info("POST data	: %s", data)

		# Check	URL
		if self.path !=	'/smarthome':
			self.send_response(401,	"invalid URL")
			self.end_headers()
			return

		# Get Input	Data
		input_data = data.get('inputs')
		if input_data == None:
			self.send_response(401,	"missing intent")
			self.end_headers()
			return

		# Get Intent & Payload Data
		intent_data	= input_data[0]['intent']

		# Check	Intent Data
		if intent_data == 'action.devices.SYNC':
			response_result	= self.do_sync(data['requestId'])
		elif intent_data ==	'action.devices.QUERY':
			payload_data = input_data[0]['payload']
			response_result	= self.do_query(data['requestId'], payload_data['devices'])
		elif intent_data ==	'action.devices.EXECUTE':
			payload_data = input_data[0]['payload']
			response_result	= self.do_execute(data['requestId'], payload_data['commands'])

		self.send_response(200)
		self.end_headers()
		self.wfile.write(json.dumps(response_result))
		logging.info("POST response	: %s", json.dumps(response_result))

		# Trigger timer for REQUEST_SYNC
		if intent_data == 'action.devices.SYNC':
			threading.Timer(REQUEST_SYNC_DURATION, self.do_requestsync).start()

		return

	# REQUEST_SYNC
	def do_requestsync(self):
		request_sync_header = {'Content-Type': 'application/json'}
		request_sync_body = {'agentUserId': AGENT_USER_ID}

		logging.debug("REQUEST_SYNC : %s", json.dumps(request_sync_body))
		resp = requests.post(requestSyncEndpoint + API_KEY, headers=request_sync_header, json=request_sync_body)
		logging.debug("RESP : %s", resp.json())
		return

	# SYNC
	def	do_sync(self, requestId):
		deviceProperty = []
		respProps =	{
			'requestId': requestId,
			'payload': {
				'agentUserId': AGENT_USER_ID,
				'devices': deviceProperty
			}
		}

		# Update Device	Property Information
		for	one_property in	devicePropertys:
			logging.debug("SYNC	: id %s, name %s", one_property['id'], one_property['name'])
			deviceProperty.append({'id': one_property['id'],  'type': one_property['type'],	'traits': one_property['traits'], 'name': one_property['name'],	'willReportState': True})

		return respProps

	# QUERY
	def	do_query(self, requestId, inDevicesInfo):
		respStatus = {}
		deviceStates = {
			'requestId': requestId,
			'payload': {
				'devices': respStatus
			}
		}

		logging.info("QUERY	: %s", inDevicesInfo)

		for	one_device_info	in inDevicesInfo:
			# Find matched device ID
			for	one_device in devicePropertys:
				if one_device['id']	== int(one_device_info['id']):
					logging.debug("QUERY : device %s, status %s", one_device['id'],	one_device['status'])
					respStatus.update({one_device['id']: {'on':	one_device['status'], 'online':	'true'}})

		return deviceStates

	# EXECUTE
	def	do_execute(self, requestId,	commands):
		respCommands = []
		responseBody = {
			'requestId': requestId,
			'payload': {
				'commands':	respCommands
			}
		}

		logging.info("EXECUTE :	%s", commands)

		for	one_command	in commands:
			for	one_device_info	in one_command['devices']:
				for	one_execution in one_command['execution']:
					logging.debug("EXECUTE : device %s, execution	%s", one_device_info['id'],	one_execution['command'])

					# Find matched device ID
					for	one_device in devicePropertys:
						if one_device['id']	== int(one_device_info['id']):
							# Power	On Off Command
							if one_execution['command']	== 'action.devices.commands.OnOff':
								do_PowerOnOff(one_device, one_execution['params']['on'])

						respCommands.append({'ids':	[one_device['id']],	'status': "SUCCESS"})

		return responseBody



# Fauxmo Main Handler
class fauxmo_device_handler(object):
	"""Publishes the on/off	state requested,
	   and the IP address of the Echo making the request.
	"""
	def	__init__(self, name):
		self.name =	name

	def	on(self, client_address, name):
		logging.debug("%s from %s on", name, client_address)
		for	one_device in devicePropertys:
			if name	== one_device['name']['name']:
				# Power	On Command
				do_PowerOnOff(one_device, True)
		return True

	def	off(self, client_address, name):
		logging.debug("%s from %s off",	name, client_address)
		for	one_device in devicePropertys:
			if name	== one_device['name']['name']:
				# Power	Off	Command
				do_PowerOnOff(one_device, False)
		return True

	def	get(self, client_address, name):
		on_off_status =	2
		return on_off_status


if __name__	== '__main__':
	from BaseHTTPServer	import HTTPServer
	server = HTTPServer(('localhost', 4003), GetHandler)
	logging.debug("Starting	server at http://localhost:4003")

	# Start	a thread with the server --	that thread	will then start	one
	# more thread for each request
	server_thread =	threading.Thread(target=server.serve_forever)
	# Exit the server thread when the main thread terminates
	server_thread.daemon = True
	server_thread.start()

	# Startup the fauxmo server
	fauxmo.DEBUG = False
	p =	fauxmo.poller()
	u =	fauxmo.upnp_broadcast_responder()
	u.init_socket()
	p.add(u)

	# Register the device callback as a	fauxmo handler
	for	one_property in	devicePropertys:
		fauxmo.fauxmo(one_property['name']['name'],	u, p, None,	one_property['id']+5200, action_handler=fauxmo_device_handler(""))

	# Loop and poll	for	incoming Echo requests
	logging.debug("Entering	fauxmo polling loop")
	while True:
		try:
			# Allow	time for a ctrl-c to stop the process
			p.poll(100)
			time.sleep(0.1)
		except Exception, e:
			logging.critical("Critical exception: "	+ str(e))
			break

	logging.debug("Exit	program")
