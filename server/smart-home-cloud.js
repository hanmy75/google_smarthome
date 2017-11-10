
const bodyParser = require('body-parser');
const express = require('express');
const fetch = require('node-fetch');
const morgan = require('morgan');
const session = require('express-session');

// internal app deps
const app = express();
app.use(morgan('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));
app.set('trust proxy', 1); // trust first proxy
app.use(session({
  genid: function (req) {
    return Math.floor(Math.random() * 10000000000000000000000000000000000000000).toString(36)
  },
  secret: 'xyzsecret',
  resave: false,
  saveUninitialized: true,
  cookie: {secure: false}
}));
const deviceConnections = {};
//const requestSyncEndpoint = 'https://homegraph.googleapis.com/v1/devices:requestSync?key=';
const appPort = "4003";

//////////////////////////
// Define device property
//////////////////////////
const deviceProperty = {
	devices: [
	{
		id: "1",
		type: "action.devices.types.LIGHT",
		traits: [
		    "action.devices.traits.OnOff",
		],
		name: {
		    name: "window"
		},
		willReportState: true
	},
	{
		id: "2",
		type: "action.devices.types.LIGHT",
		traits: [
		    "action.devices.traits.OnOff",
		],
		name: {
		    name: "center"
		},
		willReportState: true
	},
	{
		id: "3",
		type: "action.devices.types.LIGHT",
		traits: [
		    "action.devices.traits.OnOff",
		],
		name: {
		    name: "table"
		},
		willReportState: true
	},
	{
		id: "4",
		type: "action.devices.types.SWITCH",
		traits: [
		    "action.devices.traits.OnOff"
		],
		name: {
		    name: "TV"
		},
		willReportState: true
	}
	]
}

//////////////////////////
// Define device status
//////////////////////////
let deviceStatus = {
    devices: {
        "1": {
            on: true,
            online: true
        },
        "2": {
            on: true,
            online: true
        },
        "3": {
            on: true,
            online: true
        },
        "4": {
            on: true,
            online: true,
        }
    }
}

function registerAgent(app) {
  console.log('smart-home-app registerAgent');

  app.post('/smarthome', function (request, response) {
    console.log('post /smarthome', request.headers);
    let reqdata = request.body;
    console.log('post /smarthome', JSON.stringify(reqdata));

    if (!reqdata.inputs) {
      response.status(401).set({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
      }).json({error: "missing inputs"});
    }
    for (let i = 0; i < reqdata.inputs.length; i++) {
      let input = reqdata.inputs[i];
      let intent = input.intent;
      if (!intent) {
        response.status(401).set({
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }).json({error: "missing inputs"});
        continue;
      }
      switch (intent) {
        case "action.devices.SYNC":
          console.log('post /smarthome SYNC');

          sync({
            requestId: reqdata.requestId
          }, response);
          break;
        case "action.devices.QUERY":
          console.log('post /smarthome QUERY');

          query({
            requestId: reqdata.requestId,
            devices: input.payload.devices
          }, response);

          break;
        case "action.devices.EXECUTE":
          console.log('post /smarthome EXECUTE');

          exec({
            requestId: reqdata.requestId,
            commands: input.payload.commands
          }, response);

          break;
        default:
          response.status(401).set({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
          }).json({error: "missing intent"});
          break;
      }
    }
  });
  /**
   * Enables prelight (OPTIONS) requests made cross-domain.
   */
  app.options('/smarthome', function (request, response) {
    response.status(200).set({
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }).send('null');
  });

  function sync(data, response) {
    console.log('sync', JSON.stringify(data));

    let deviceProps = {
        requestId: data.requestId,
        payload: deviceProperty
    };

    console.log('sync response', JSON.stringify(deviceProps));
    response.status(200).json(deviceProps);
    return deviceProps;
  }

  function query(data, response) {
    console.log('query', JSON.stringify(data));

    let deviceStates = {
        requestId: data.requestId,
        payload: deviceStatus
    };

    console.log('query response', JSON.stringify(deviceStates));
    response.status(200).json(deviceStates);
    return deviceStates;
  }

  function getDeviceIds(devices) {
    let deviceIds = [];
    for (let i = 0; i < devices.length; i++) {
      if (devices[i] && devices[i].id)
        deviceIds.push(devices[i].id);
    }
    return deviceIds;
  }

  function exec(data, response) {
    console.log('exec', JSON.stringify(data));
    let respCommands = [];

    for (let i = 0; i < data.commands.length; i++) {
      let curCommand = data.commands[i];
      for (let j = 0; j < curCommand.execution.length; j++) {
            let curExec = curCommand.execution[j];
            let devices = curCommand.devices;
	    if (curExec.command === "action.devices.commands.OnOff") {
	        for (let k = 0; k < curCommand.devices.length; k++) {
	            let curDevice = curCommand.devices[k];
	            if (curDevice.id === "1") {
	                //devices.fan.on = curExec.params.on;
	            } else if (curDevice.id === "2") {
	                //devices.lights.on = curExec.params.on;
	            }
	            respCommands.push({ids: [ curDevice.id ], status: "SUCCESS"});
	        }
	    } else if (curExec.command === "action.devices.commands.ColorAbsolute") {
	        for (let k = 0; k < curCommand.devices.length; k++) {
	            let curDevice = curCommand.devices[k];
	            if (curDevice.id === "2") {
	                //devices.lights.spectrumRGB = curExec.params.color.spectrumRGB;
	            }
	            respCommands.push({ids: [ curDevice.id ], status: "SUCCESS"});
	        }
	    }
      }
    }
    
    let resBody = {
      requestId: data.requestId,
      payload: {
        commands: respCommands
      }
    };
    console.log('exec response', JSON.stringify(resBody));
    response.status(200).json(resBody);
    return resBody;
  }

  registerAgent.exec = exec;
}

const server = app.listen(appPort, function () {
  const host = server.address().address;
  const port = server.address().port;
  console.log('Smart Home Cloud and App listening at %s:%s', host, port);

  registerAgent(app);
});
