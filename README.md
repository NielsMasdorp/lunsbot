# lunsbot

Slack bot that decides where to eat for lunch.

## Usage

### Slack configuration

- Create an Slack app @ https://api.slack.com/apps?new_app=1 and add it to your workspace.
- Create a bot user with your desired name (this bot will be the access point of the application).
- Go to "Install App" under "Settings" and export the Bot user OAuth token to your environment
```
export SLACK_LUNSBOT_API_KEY='bot oauth token'
```
- Retrieve the ID of the bot @ https://api.slack.com/methods/bots.info and remember it, you need it to initialise the script

### Foursquare configuration
- Create an app @ https://foursquare.com/developers/apps and retrieve your client id and client secret to authenticate the API
- export these variables: 
```
export FOURSQUARE_CLIENT_ID='id'
export FOURSQUARE_CLIENT_SECRET='secret'
```

### Google Maps configuration
- Create an API key @ https://developers.google.com/maps/documentation/maps-static/get-api-key
- Export the API key: `export GOOGLE_MAPS_API_KEY='key'`

### Dependencies
- Python 2+
- requests: https://pypi.org/project/requests/
- slackclient: https://pypi.org/project/slackclient/

### Run

Use your previously acquired bot id and location and optional radius in meters

`python slack-lunsbot.py --botid=HS3284S --loc=52.0895722,5.1110258 --radius=350`

More information on the arguments can be found with:

`python slack-lunsbot.py -h`

### Finally
Add lunsbot to one of your channels in slack and activate by typing `@lunsbot zoek luns`

License
====
```
The MIT License (MIT)

Copyright (c) 2018 Niels Masdorp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
