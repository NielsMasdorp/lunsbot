import argparse
import sys
import os
import requests
import time
import random
from slackclient import SlackClient

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--botid', required=True,
                    help='ID of the slack bot, can be found with the https://api.slack.com/methods/bots.info request')
parser.add_argument('--loc', required=True,
                    help='Latitude and longitude seperated by a comma (e.g. 52.0895722,5.1110258')
parser.add_argument(
    '--radius', help='Radius in meters to search for lunch venues')
args = parser.parse_args()

# Required arguments
botId = None
location = None

# Radius in meters, defaults to 350
radius = None

# API keys
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')
MAPS_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')

# Slack client
print(os.environ.get('SLACK_LUNSBOT_API_KEY'))
slack_client = SlackClient(os.environ.get('SLACK_LUNSBOT_API_KEY'))

# The command to respond to (e.g. "@lunsbot search")
searchCommand = 'search'

# Base URLS for foursquare
FOURSQUARE_EXPLORE_URL = 'https://api.foursquare.com/v2/venues/explore?client_id={0}&client_secret={1}&ll={2}&openNow=1&radius={3}&section=food&v=20181128'
FOURSQUARE_DETAILS_URL = 'https://api.foursquare.com/v2/venues/{0}?client_id={1}&client_secret={2}&v=20181128'

# URL for retrieval of static map images
GOOGLE_MAPS_STATIC_MAPS_URL = 'http://maps.googleapis.com/maps/api/staticmap?center={0}&size=800x800&zoom=18&sensor=true&mapType=hybrid&markers=color:red%7Clabel:Here%7C{1}&key={2}'


def handle_command(command, channel):
    if command == searchCommand:
        send_message_to_chat(message='Searching for popular venue within {0} meters'.format(
            radius), channel=channel)
        venues = explore_venues()
        if len(venues) == 0:
            send_message_to_chat(
                message='No venues found, you\'ll be starving today..', channel=channel)
        else:
            randomVenue = random.choice(venues)
            distanceToVenue = randomVenue.get(
                'venue').get('location').get('distance')
            selectedVenue = get_venue_details(
                venueId=randomVenue.get('venue').get('id'))
            lat = selectedVenue.get('location').get('lat')
            lng = selectedVenue.get('location').get('lng')
            venueLatLng = '{0},{1}'.format(lat, lng)
            venueRating = selectedVenue.get(
                'rating') if selectedVenue.get('rating') else 'unknown'
            venueName = selectedVenue.get('name')
            venueUrl = selectedVenue.get('canonicalUrl')
            send_message_to_chat(message='I have found a spot named: {0}, at {1} meter walking distance. \n\n Avarage rating: {2}. Link: {3}'.format(
                venueName, distanceToVenue, venueRating, venueUrl), channel=channel)
            if lat and lng:
                mapUrl = GOOGLE_MAPS_STATIC_MAPS_URL.format(
                    venueLatLng, venueLatLng, MAPS_KEY)
                send_attachment_to_chat(
                    attachments=[{"title": "Location on map", "image_url": mapUrl}])
    else:
        send_message_to_chat(
            message='Use \"@lunsbot search\" to search for spots', channel=channel)

# Send a message to a channel as the bot


def send_message_to_chat(message, channel):
	slack_client.api_call("chat.postMessage",
						channel=channel, text=message, as_user=True)

# Send attachment to a channel as the bot


def send_attachment_to_chat(attachments):
	slack_client.api_call("chat.postMessage", channel=channel,
						text='', attachments=attachments, as_user=True)

# Return recommended venues nearby


def explore_venues():
	venueRequest = requests.get(FOURSQUARE_EXPLORE_URL.format(
		FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET, location, radius))
	return venueRequest.json().get('response').get('groups')[0].get('items')

# Return the details of a venue with a provided id


def get_venue_details(venueId):
	detailsRequest = requests.get(FOURSQUARE_DETAILS_URL.format(
		venueId, FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET))
	return detailsRequest.json().get('response').get('venue')

# Parse the message that was sent to the bot with "@lunsbot $message"


def parse_slack_output(slack_rtm_output):
	output_list = slack_rtm_output
	if output_list and len(output_list) > 0:
		for output in output_list:
			if output and 'text' in output and "<@{0}>".format(botId) in output['text']:
				# return text after the @ mention, whitespace removed
				return output['text'].split("<@{0}>".format(botId))[1].strip().lower(), \
					output['channel']
	return None, None


# Main function
if __name__ == "__main__":
	READ_WEBSOCKET_DELAY = 1
	if slack_client.rtm_connect():
		print("Lunsbot running!")
		args = parser.parse_args()
		botId = args.botid
		location = args.loc
		radius = args.radius if args.radius else 350
		while True:
			command, channel = parse_slack_output(slack_client.rtm_read())
			if command and channel:
				handle_command(command, channel)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Invalid Slack token or bot ID?")

