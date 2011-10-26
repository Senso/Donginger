
import re
import twitter
from random import randrange

from plugin import Plugin

class Twit(Plugin):
	def __init__(self, dong, conf):
		super(Twit, self).__init__(dong, conf)
		self.api = twitter.Api(consumer_key=self.conf['consumer_key'],consumer_secret=self.conf['consumer_secret'],access_token_key=self.conf['access_token_key'],access_token_secret=self.conf['access_token_secret'])
		
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
		
	def add_tag(self, callback, who, tag):
		"""Add a tag to the list used by <random tweet>."""
		
		if len(tag) > 2:
			if tag[0] == '#':
				tag = tag[1:]
			tag = tag.strip('\r')
			self.dong.db.insert('twitter_tags', {'name': tag})
			return 'Tag added.'
			
	def del_tag(self, callback, who, tag):
		"""Deletes a tag from the list used by <random tweet>."""
		
		self.dong.db.delete_by_name('twitter_tags', ('name', tag))
		return 'Tag deleted.'
		
	def add_target(self, callback, who, name):
		"""Add a twitter account to the Shitlist."""
		
		if len(name) > 2:
			if name[0] == '@':
				name = name[1:]
			self.dong.db.insert('twitter_hitlist', {'name': name})
			return 'Target added to Shitlist.'
			
	def del_target(self, callback, who, name):
		"""Removes a twitter account from the Shitlist."""
		
		dong.db.delete_by_name('twitter_hitlist', ('name', name))
		return 'Target removed from Shitlist.'
		
	def get_random_tags(self):
		num = randrange(1,4)
		tags = []
		for i in range(1, num):
			rand_tag = self.dong.db.get_random_row('twitter_tags')
			rand_tag = rand_tag[1]

			if rand_tag not in tags:
				if rand_tag[0] == '#':
					tags.append(rand_tag)
				else:
					tags.append('#' + rand_tag)
		if tags:
			return ' '.join(tags)
		
	def random_tweet(self, callback, who, msg):
		"""Posts a tweet to a random members of the Shitlist and appends random tags."""
		
		target = self.dong.db.get_random_row('twitter_hitlist')
		target = target[1]
		tags = self.get_random_tags()
		if tags:
			msg += ' ' + tags
		return self.post_tweet_to(target, msg)
		
	def riot_tweet(self, callback, who, msg):
		"""Tweets the ouput of @riotkrrn"""
		
		riot = re.search('random tweet (.+)', callback)
		if riot:
			return self.random_tweet(callback, who, riot.group(1))
			
	def post_tweet_to(self, who, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				str = "@%s %s" % (who, msg)
				status = self.api.PostUpdate(str)
				return str
			except Exception,e:
				print "HTTP error: %s" % e

	def post_tweet(self, callback, who, msg):
		"""Posts a raw tweet."""
		
		msg = self.remove_unicode(msg)
		if msg:
			try:
				status = self.api.PostUpdate(msg)
			except Exception,e:
				print "HTTP 500 error: %s" % e
				
				

