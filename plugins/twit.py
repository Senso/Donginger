import twitter

class Twit:
	def __init__(self, bot):
		self.bot = bot
		self.api = twitter.Api(consumer_key=bot.modules['twitter']['consumer_key'],consumer_secret=bot.modules['twitter']['consumer_secret'],access_token_key=bot.modules['twitter']['access_token_key'],access_token_secret=bot.modules['twitter']['access_token_secret'])
		
	def remove_unicode(self, str):
		newstr = ''
		for c in str:
			if ord(c) > 127: pass
			else: newstr += c
		return newstr

	def getFollowers(self):
		derp = []
		try:
			for i in self.api.GetFollowers():
				derp.append(i.screen_name)
			return ', '.join(derp)
		except: return ''

	def postTweetTo(self, who, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				status = self.api.PostUpdate("@%s %s" % (who, msg))
			except Exception,e:
				print "HTTP error: %s" % e

	def postTweet(self, msg):
		msg = self.remove_unicode(msg)
		if msg:
			try:
				status = self.api.PostUpdate(msg)
			except Exception,e:
				print "HTTP 500 error: %s" % e
