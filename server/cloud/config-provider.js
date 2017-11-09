// Copyright 2017, Google, Inc.
// Licensed under the Apache License, Version 2.0 (the 'License');
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var Config = {};

Config.devPortSmartHome = "4003";
Config.smartHomeProviderGoogleClientId = "RKkWfsi0Z9"; // client id that Google will use
Config.smartHomeProvideGoogleClientSecret = "eToBzeBT7OwrPQO8mZHsZtLp1qhQbe"; // client secret that Google will use
Config.smartHomeProviderApiKey = "AIzaSyBHnS2UwDuHfQd6HX6ce5WoDFB4ZT0Hhe8"; // client API Key generated on the console

function init() {
  console.log("config: ", Config);
}
init();

exports.devPortSmartHome = Config.devPortSmartHome;
exports.smartHomeProviderGoogleClientId = Config.smartHomeProviderGoogleClientId;
exports.smartHomeProvideGoogleClientSecret = Config.smartHomeProvideGoogleClientSecret;
exports.smartHomeProviderApiKey = Config.smartHomeProviderApiKey;
