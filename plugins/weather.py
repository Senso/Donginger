from plugin import Plugin
import urllib

class Weather(Plugin):
	""" Weather Underground plugin. """
	
	def __init__(self, dong, conf):
		super(Weather, self).__init__(dong, conf)

	def db_loc(self, who, loc=None):
		# Check if we already have that user in the DB
		table = self.dong.db.tables['weather']

		q = self.dong.db.session.query(table).filter(getattr(table.c, 'user') == who)
		is_in_db = q.all()

		if loc is not None and is_in_db:
			# For some reason .update() stopped working, fuck it
			self.dong.db.delete('weather', (0, is_in_db[0][0]))
			self.dong.db.insert('weather', {'user': who, 'location': loc})
		elif loc is not None and not is_in_db:
			self.dong.db.insert('weather', {'user': who, 'location': loc})
			
		try:
			return str(is_in_db[0][1])
		except:
			return None
		
	def fetch_weather(self, callback, who, loc):
		"""<weather location> returns the weather for that location. Not providing a location makes it returns the weather of your last used location."""
		
		# Fetch cached location if not provided
		if not loc:
			cached_loc = self.db_loc(who)
			if not cached_loc:
				return self.__doc__

		else:
			self.db_loc(who, loc)
		
		loc = urllib.quote(loc)
		
		try:
			results = self.get_json("http://api.wunderground.com/api/%s/geolookup/conditions/forecast/q/%s.json" %
								(self.conf['weather_underground_key'], loc))

			data = {}
			data['city'] = results['location']['city']
			data['temp'] = results['current_observation']['temperature_string']
			data['condition'] = results['current_observation']['weather']
			data['humidity'] = results['current_observation']['relative_humidity']
			data['wind'] = results['current_observation']['wind_mph']
			try:
				data['rain_in'] = float(results['current_observation']['precip_today_in'])
			except:
				data['rain_in'] = 0.0
			try:
				data['rain_mm'] = float(results['current_observation']['precip_today_metric'])
			except:
				data['rain_mm'] = 0.0
			
			if data['rain_in'] > 0.00 and data['rain_mm'] > 0.00:
				output = '%(city)s: %(condition)s, %(temp)s, %(humidity)s humidity, %(wind)s MPH winds. Rain today: %(rain_in)s in (%(rain_mm)s mm).' % data
			else:
				output = '%(city)s: %(condition)s, %(temp)s, %(humidity)s humidity, %(wind)s MPH winds.' % data
			
			return output
		except Exception, e:
			# Most likely not JSON
			#print 'Weather JSON error:', e
			return 'Error fetching results, most likely an ambiguous location.'

