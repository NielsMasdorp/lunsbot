import argparse
import sys
import os
import requests
import time
import random
from slackclient import SlackClient

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--botid', required = True, help='ID of the slack bot, can be found with the https://api.slack.com/methods/bots.info request')
parser.add_argument('--loc', help='Latitude and longitude seperated by a comma (e.g. 52.0895722,5.1110258')
parser.add_argument('--radius', help='Radius in meters to search for lunch venues')

# Foursquare API credentials
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')

# Maps API Key
MAPS_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

# Bot id
botId = ''

# Bot mention string
AT_BOT = "<@" + botId + ">"

# Slack client
slack_client = SlackClient(os.environ.get('SLACK_LUNSBOT_API_KEY'))

# Location to search venues for
location = '52.0895722,5.1110258'

# Radius in meters to search venues in
radius = 350

# The command to respond to (e.g. "@lunsbot zoek luns")
searchCommand = 'zoek luns'

# Base URLS for foursquare
FOURSQUARE_EXPLORE_URL = 'https://api.foursquare.com/v2/venues/explore?client_id={0}&client_secret={1}&ll={2}&openNow=1&radius={3}&section=food&v=20181128'
FOURSQUARE_DETAILS_URL = 'https://api.foursquare.com/v2/venues/{0}?client_id={1}&client_secret={2}&v=20181128'

# URL for retrieval of static map images
GOOGLE_MAPS_STATIC_MAPS_URL = 'http://maps.googleapis.com/maps/api/staticmap?center={0}&size=800x800&zoom=18&sensor=true&mapType=hybrid&markers=color:red%7Clabel:Here%7C{1}&key={2}'

def handle_command(command, channel):
    if command == searchCommand:
        sendMessageToChat(message = 'Ik ga voor je op zoek, moment', channel = channel)
        venues = exploreVenues()
        if len(venues) == 0:
            sendMessageToChat(message = 'Geen plekken gevonden waar je kan eten :(', channel = channel)
        else:
            randomVenue = random.choice(venues)
            distanceToVenue = randomVenue.get('venue').get('location').get('distance')
            selectedVenue = getVenueDetails(venueId = randomVenue.get('venue').get('id'))
            lat = selectedVenue.get('location').get('lat')
            lng = selectedVenue.get('location').get('lng')
            venueLatLng = '{0},{1}'.format(lat, lng)
            venuesAddress = '{0}, {1}, {2}'.format(selectedVenue.get('location').get('address'), selectedVenue.get('location').get('city'), selectedVenue.get('location').get('country')) 
            venuePrice = selectedVenue.get('price')
            venuePriceMessage = venuePrice.get('message') if venuePrice else 'onbekend'
            venueRating = selectedVenue.get('rating') if selectedVenue.get('rating') else 'onbekend'
            venueName = selectedVenue.get('name')
            venueUrl = selectedVenue.get('canonicalUrl')
            sendMessageToChat(message = 'Het is geworden: {0}. \n\n Dit is {1} meter lopen. \n\n Deze plek krijgt een {2} en de prijsklasse is: {3} \n\n Meer informatie: {4}'.format(venueName, distanceToVenue, venueRating, venuePriceMessage, venueUrl), channel = channel)
            if lat is not None and lng is not None:
                mapUrl = GOOGLE_MAPS_STATIC_MAPS_URL.format(venueLatLng, venueLatLng, MAPS_KEY)
                sendAttachmentToChat(attachments = [{"title": "Locatie op kaart","image_url": mapUrl}])
    else:
        sendMessageToChat(message = 'Zo werkt het niet, knul. Probeer: \"zoek luns\"', channel = channel)

# Send a message to a channel as the bot
def sendMessageToChat(message, channel):
    slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

# Send attachment to a channel as the bot
def sendAttachmentToChat(attachments):
    slack_client.api_call("chat.postMessage", channel=channel, text='', attachments=attachments, as_user=True)

# Return recommended venues nearby
def exploreVenues():
    venueRequest = requests.get(FOURSQUARE_EXPLORE_URL.format(FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET, location, radius))
    return venueRequest.json().get('response').get('groups')[0].get('items')

# Return the details of a venue with a provided id
def getVenueDetails(venueId):
    detailsRequest = requests.get(FOURSQUARE_DETAILS_URL.format(venueId, FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET))
    return detailsRequest.json().get('response').get('venue')

# Parse the message that was sent to the bot with "@lunsbot $message"
def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


# Main function
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Lunsbot connected and running!")
        # Initialize optional command arguments
        args = parser.parse_args()
        botId = args.botid
        radius = args.radius if args.radius else 350
        location = args.loc if args.loc else '52.0895722,5.1110258'
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

