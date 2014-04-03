
import re
import time
#import twitter
from twitter import *
from random import randrange, choice

from plugin import Plugin

class Twit(Plugin):
	def __init__(self, dong, conf):
		super(Twit, self).__init__(dong, conf)
		#self.api = twitter.Api(consumer_key=self.conf['consumer_key'],consumer_secret=self.conf['consumer_secret'],access_token_key=self.conf['access_token_key'],access_token_secret=self.conf['access_token_secret'])
		self.api = Twitter(auth=OAuth(self.conf['access_token_key'], self.conf['access_token_secret'],
							self.conf['consumer_key'], self.conf['consumer_secret']))
		#self.replies = open(self.conf['shit_replies']).readlines()
		
	def remove_unicode(self, str):
		newstr = ''
		for c in str:
			if ord(c) > 127: pass
			else: newstr += c
		return newstr

	def get_followers(self):
		derp = []
		try:
			for i in self.api.GetFollowers():
				derp.append(i.screen_name)
			return ', '.join(derp)
		except: return ''
		
	def add_tag(self, callback, who, tag, obj):
		"""Add a tag to the list used by <random tweet>."""

		if not self.check_perms(obj):
			return
		
		if len(tag) > 2:
			if tag[0] == '#':
				tag = tag[1:]
			tag = tag.strip('\r')
			self.dong.db.insert('twitter_tags', {'name': tag})
			return 'Tag added.'
			
	def del_tag(self, callback, who, tag, obj):
		"""Deletes a tag from the list used by <random tweet>."""

		if not self.check_perms(obj):
			return
		
		self.dong.db.delete_by_name('twitter_tags', ('name', tag))
		return 'Tag deleted.'
		
	def add_target(self, callback, who, name, obj):
		"""Add a twitter account to the Shitlist."""
		
		if not self.check_perms(obj):
			return

		if len(name) > 2:
			if name[0] == '@':
				name = name[1:]
			self.dong.db.insert('twitter_hitlist', {'name': name})
			return 'Target added to Shitlist.'
			
	def del_target(self, callback, who, name, obj):
		"""Removes a twitter account from the Shitlist."""

		if not self.check_perms(obj):
			return
		
		self.dong.db.delete_by_name('twitter_hitlist', ('name', name))
		return 'Target removed from Shitlist.'
		
	def get_random_tags(self):
		num = randrange(2,5)
		tags = []
		for i in range(1, num):
			if i == 1:
				tt = self.get_random_trend()
				if tt:
					tags.append('#' + tt)
			else:
				rand_tag = self.dong.db.get_random_row('twitter_tags')
				rand_tag = rand_tag[1]

				if rand_tag not in tags:
					if rand_tag[0] == '#':
						tags.append(rand_tag)
					else:
						tags.append('#' + rand_tag)
		if tags:
			return ' '.join(tags)
		else:
			return ''
		
	def random_tweet(self, callback, who, msg, obj):
		"""Posts a tweet to a random members of the Shitlist and appends random tags."""

		if not self.check_perms(obj):
			return
		
		if randrange(1,100) < 50:
			target = self.dong.db.get_random_row('twitter_hitlist')
			target = target[1]
		else:
			#while 1: # Oh this is bad
			target = self.get_random_target()

		tags = self.get_random_tags()
		
		pre_tweet = len('@%s %s' % (target, msg))
		for x in tags.split(' '):
			if len(x) + pre_tweet <= 139:
				msg += ' ' + x
			
		#if tags:
		#	msg += ' ' + tags
		#print 'target', target
		#print 'tags', str(tags)
		return self.post_tweet_to(target, msg)
		
	def riot_tweet(self, callback, who, msg, obj):
		"""Tweets the ouput of @riotkrrn. Only works if you're in the same room as Donginger."""
		
		if not self.check_perms(obj):
			return

		riot = re.search('randtweet (.+)', callback)
		if riot:
			return self.random_tweet(callback, who, riot.group(1), obj)
			
	def post_tweet_to(self, who, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				str = "@%s %s" % (who, msg)
				if len(str) > 140:
					return
				status = self.api.statuses.update(status=str)
				return str
			except Exception,e:
				print "HTTP error: %s" % e

	def post_tweet(self, callback, who, msg, obj):
		"""Posts a direct tweet."""
	
		if not self.check_perms(obj):
			return

		msg = self.remove_unicode(msg)
		if len(msg) < 140:
			try:
				#status = self.api.PostUpdate(msg)
				self.api.statuses.update(status=msg)
			except Exception,e:
				print "HTTP 500 error: %s" % e

	def check_perms(self, objnum):
		"""No players allowed!"""

		if objnum not in self.conf['whitelist']:
			return False
		return True
				
	def show_shitlist(self, callback, who, arg):
		"""Shows the full Shitlist (potential random targets of nasty tweets)"""
		
		shitlist = self.dong.db.select_all('twitter_hitlist')
		shit_names = []
		if shitlist:
			for i in shitlist:
				shit_names.append(i[1])
			return ', '.join(shit_names)
			
	def show_tags(self, callback, who, arg):
		"""Shows the full list of random tags that can be appended to random tweets"""
		
		tags = self.dong.db.select_all('twitter_tags')
		tag_names = []
		if tags:
			for i in tags:
				tag_names.append(i[1])
			return ', '.join(tag_names)
			
	def get_random_target(self):
		user = None
		while True:
			tag = self.dong.db.get_random_row('twitter_tags')
			tweets = self.api.search.tweets(q='#' + tag[1])
			frtweet = choice(tweets['statuses'])
			user = frtweet['user']['screen_name']
			if user != 'don_ginger' and user != '@don_ginger':
				break
			else:
				time.sleep(1)
		return user

	def get_random_trend(self):
		# WOEID for USA
		trends = self.api.trends.place(_id=23424977)
		valids = []
		if trends:
			for t in trends[0]['trends']:
				ugh = t['query']
				if ugh and ugh[0:3] == '%23':
					ugh = ugh.replace('%23', '')
					valids.append(ugh)
		if valids:
			return choice(valids)
		return None
