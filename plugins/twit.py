import twitter


class Twit:
	def __init__(self, name, dong):
		self.name = name
		self.dong = dong
		self.conf = self.dong.plugins_conf[name]
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
			dong.db.insert('twitter_tags', {'name': tag})
			
	def del_tag(self, tag):
		dong.db.delete('twitter_tags', {'name': tag})
		
	def get_random_tags(self):
		num = random.randrange(1,4)
		tags = []
		for i in range(1, num):
			self.dong.db.cu.execute("select * from ? order by random() limit 1", (self.conf['db_tables']['twitter_tags'],))
			tag = dba.cu.fetchone()
			if tag[0] not in tags:
				if tag[0][0] == '#':
					tags.append(tag[0])
				else:
					tags.append('#' + tag[0])
		if tags:
			return ' '.join(tags)
		
	def random_tweet(self, msg):
		self.dong.db.cu.execute("select * from ? order by random() limit 1", (self.conf['db_tables']['twitter_hitlist']))
		target = self.dong.db.cu.fetchone()[0]
		tags = self.get_random_tags()
		if tags:
			msg += ' ' + tags
		self.post_tweet_to(target, msg)

	def post_tweet_to(self, who, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				status = self.api.PostUpdate("@%s %s" % (who, msg))
			except Exception,e:
				print "HTTP error: %s" % e

	def post_tweet(self, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				status = self.api.PostUpdate(msg)
			except Exception,e:
				print "HTTP 500 error: %s" % e
				
				

