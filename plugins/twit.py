import twitter

class Twit:
	def __init__(self, name, dong):
		self.dong = dong
		conf = self.dong.modules[name]
		self.api = twitter.Api(consumer_key=conf['consumer_key'],consumer_secret=conf['consumer_secret'],access_token_key=conf['access_token_key'],access_token_secret=conf['access_token_secret'])
		
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
			try: #unique constraint
				if tag[0] == '#':
					tag = tag[1:]
				tag = tag.strip('\r')
				self.dong.db.cu.execute("insert into ?(name) values(?)", (dong.db_tables['tags'], tag.lower(),))
			except: pass
			
	def del_tag(self, tag):
		try:
			self.dong.db.cu.execute("delete from ? where name = ?", (dong.db_tables['tags'], tag.lower(),))
		except: pass
		
	def get_random_tags(self):
		num = random.randrange(1,4)
		tags = []
		for i in range(1, num):
			self.dong.db.cu.execute("select * from ? order by random() limit 1", (dong.db_tables['tags'],))
			tag = dba.cu.fetchone()
			if tag[0] not in tags:
				if tag[0][0] == '#':
					tags.append(tag[0])
				else:
					tags.append('#' + tag[0])
		if tags:
			return ' '.join(tags)
		
	def random_tweet(self, msg):
		self.dong.db.cu.execute("select * from ? order by random() limit 1", (dong.db_tables['hitlist']))
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
