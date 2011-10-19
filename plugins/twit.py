import twitter
from random import randrange

class Twit(Plugin):
	def __init__(self, name, dong):
		super(Twit, self).__init__(name, dong)
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
		
	def add_tag(self, tag):
		if len(tag) > 2:
			if tag[0] == '#':
				tag = tag[1:]
			tag = tag.strip('\r')
			self.dong.db.insert('twitter_tags', {'name': tag})
			return 'Tag added.'
			
	def del_tag(self, tag):
		self.dong.db.delete_by_name('twitter_tags', ('name', tag))
		return 'Tag deleted.'
		
	def add_target(self, name):
		if len(name) > 2:
			if name[0] == '@':
				name = name[1:]
			self.dong.db.insert('twitter_hitlist', {'name': name})
			
	def del_target(self, name):
		dong.db.delete_by_name('twitter_hitlist', ('name', name))
		
	def get_random_tags(self):
		num = random.randrange(1,4)
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
		
	def random_tweet(self, msg):
		target = self.dong.db.get_random_row('twitter_hitlist')
		target = target[1]
		tags = self.get_random_tags()
		if tags:
			msg += ' ' + tags
		return self.post_tweet_to(target, msg)

	def post_tweet_to(self, who, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				str = "@%s %s" % (who, msg)
				status = self.api.PostUpdate(str)
				return str
			except Exception,e:
				print "HTTP error: %s" % e

	def post_tweet(self, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				status = self.api.PostUpdate(msg)
			except Exception,e:
				print "HTTP 500 error: %s" % e
				
				

