import os
import time
from slackclient import SlackClient
from apixu.client import ApixuClient, ApixuException

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")
APIXU_KEY = os.environ.get("APIXU_KEY")
PALS_CHANNEL = os.environ.get("PALS_CHANNEL")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
CITY = 'Edmonton'
WEATHER_CHECK = "is it snowing?"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
apixu_client = ApixuClient(APIXU_KEY)


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    if command.startswith(WEATHER_CHECK):
        condition = get_weather()
        response  = "It's " + condition + " right now, not quite time for movie night :("

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def check_for_snow(location):
    
    condition  = get_weather(location)

    #check if condition contains 'snow' and NOT 'possible'
    return "snow" in condition.lower() and "possible" not in condition.lower()
        

def snow_message(location, channel):
    if check_for_snow(location):
        reponse = "IS SNOWING LETS GET OUR MOVIE ON!!!!!"
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def get_weather(location):
    current = apixu_client.getCurrentWeather(q=location) 
    condition = current['current']['condition']['text']
    print(condition)
    return condition
    

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """

    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        timer  = 0
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            if timer == 0:
               snow_message(CITY, PALS_CHANNEL)
            elif timer == 3600:
                timer = -1
            timer += 1
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")