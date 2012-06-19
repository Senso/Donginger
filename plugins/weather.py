from plugin import Plugin

class Wu(Plugin):
	""" Weather Underground plugin. """
	
	def __init__(self, dong, conf):
		super(Wu, self).__init__(dong, conf)
		
	def fetch_weather(self, callback, who, loc):
		"""<weather location> returns the weather for that location. Not providing a location makes it returns the weather of your last used location."""
		
		# Check if we already have that user in the DB
		table = self.dong.db.tables['weather']
		q = self.dong.db.session.query(table).filter(getattr(table.c, 'user') == who)
		
		# Fetch cached location if not provided
		if not loc:
			try:
				loc = q.all()[0][1]
			except:
				return self.__doc__
		else:
			db_loc = q.all()
			if db_loc:
				self.dong.db.update('weather', {'user': who}, {'location': loc})
			else:
				self.dong.db.insert('weather', {'user': who, 'location': loc})
		
		try:
			results = self.get_json("http://api.wunderground.com/api/%s/geolookup/conditions/forecast/q/%s.json" %
								(self.conf['weather_underground_key'], loc))
		except:
			# Most likely not JSON
			return
		
		return results
		#xml = self.get_json('http://www.google.com/ig/api', {'weather': loc})
		# Strip funky UTF8 characters
		#return self.process_xml(xml)