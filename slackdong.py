import os
import time
import re
import cPickle
import sys
import json
import random
import socket
import urllib2
from slackclient import SlackClient

#sys.path += ['plugins']
#from pytoon import Pytoon

BOT_TOKEN='SLACK TOKEN'

#slack_client = SlackClient(BOT_TOKEN)
dongbot_id = None

# constants
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

class DumbBot:
    def __init__(self):
        self.BOT_TOKEN=BOT_TOKEN
        self.slack_client = SlackClient(self.BOT_TOKEN)

        self.last_cata_parse = 0
        self.scrape_cata_every = 1800 # 30 minutes

    def parse_bot_commands(self, slack_events):
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = self.parse_direct_mention(event["text"])
                if user_id == self.starterbot_id:
                    return message, event["channel"]
        return None, None

    def parse_direct_mention(self, message_text):
        matches = re.search(MENTION_REGEX, message_text)
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def random_life(self, command, channel):
        try:
            with open('catagolue.data') as derp:
                all_finds = cPickle.load(derp)
                obj = random.choice(all_finds.keys())
                url = "https://catagolue.appspot.com/object/%s/%s" % (obj[0], obj[1])
                self.slack_client.api_call(
                    "chat.postMessage",
                    channel=channel,
                    text=url
                )
        except:
            pass

    def scrape_catagolue(self):
        try:
            url = 'https://catagolue.appspot.com/user/<snip>/all#discoveries'
            fd = urllib2.urlopen(url, timeout=10)
            #fd = open('cata.html', 'r')
            data = fd.read()
            self.last_cata_parse = time.time()
        except urllib2.URLError:
            return

        # Load saved object
        try:
            with open('catagolue.data') as derp:
                all_finds = cPickle.load(derp)
        except:
            all_finds = {}

        pattern = re.compile('\<a href=\"\/object\/(.+)\/(.+)\"\>')

        txt = ""

        objects = re.findall(pattern, data)
        if objects:
            for obj in objects:
                if obj not in all_finds:
                    all_finds[obj] = True
                    url = "https://catagolue.appspot.com/object/%s/%s" % (obj[0], obj[1])
                    txt = ":toot: Dionysus has found a new Life pattern! %s " % (url,)
                    print txt
        if txt:
            self.slack_client.api_call(
                "chat.postMessage",
                channel='<CHANNEL ID>',
                text=txt
            )

        with open('catagolue.data', 'wb') as derp:
            cPickle.dump(all_finds, derp)

    def handle_command(self, command, channel):
        if command.startswith('comic'):
            path = '/home/donginger/webroot/blab/static/'
            webpath = 'http://dejablabspace.com/static'
            comic = random.choice(os.listdir(path))

            response = "%s/%s" % (webpath, comic)

            att = [{"title": "random strip", "image_url": response, "thumb_url": response, "title_link": response}]

            self.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text="",
                attachments=str(att)
            )
        elif command.startswith('djbooth'):
            url = urllib2.urlopen('http://api.tspigot.net:1338/streams/moo')
            try:
                j = json.loads(url.read())
                artist = j['playing']['track']['artist']
                album = j['playing']['track']['album']
                track = j['playing']['track']['title']
                line = "Now playing *%s* by _%s_ from the album %s" % (track, artist, album)
                self.slack_client.api_call(
                    "chat.postMessage",
                    channel=channel,
                    text=line,
                )

            except Exception as e:
                print "djbooth error: %s" % e
 #       elif command.startswith('wiki') or command.startswith('randwiki'):
 #           pass
        elif command.startswith('life'):
            self.random_life(command, channel)
        else:
            self.farts(command, channel)

    def farts(self, command, channel):
        with open('ascii.txt') as farts:
            line = random.choice(farts.readlines())
            self.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=line,
            )

    def do_the_thing(self):
        if self.slack_client.rtm_connect(with_team_state=False, auto_reconnect=True):
            print("Donginger connected and running!")
            # Read bot's user ID by calling Web API method `auth.test`
            self.starterbot_id = self.slack_client.api_call("auth.test")["user_id"]
        else:
            print("Connection failed.")

    def read_the_thing(self):
        try:
            command, channel = self.parse_bot_commands(self.slack_client.rtm_read())
            #print "channel: %s" % channel
            if command:
                self.handle_command(command, channel)
        except socket.error:
            self.slack_client.rtm_connect(with_team_state=False)
        time.sleep(1)

if __name__ == "__main__":
    s = DumbBot()
    s.do_the_thing()
    while True:
        if time.time() - s.last_cata_parse > s.scrape_cata_every:
            s.scrape_catagolue()
        s.read_the_thing()
