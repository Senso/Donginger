
import json
from plugin import Plugin
from random import choice

class Suggest(Plugin):
	def __init__(self, name, dong):
		super(Suggest, self).__init__(name, dong)
		
	def google_suggest(self, callback, who, arg):
		"""<suggest string> - returns a random Google Suggestion based on the string."""
		
		w = self.build_query('http://google.com/complete/search', {'q': arg})
		page = w.read()
		page_json = page.split('(', 1)[1][:-1]
		suggestions = json.loads(page_json)[1]
		if suggestions:
			suggestions = self.remove_lyrics(suggestions)
			random_sug = choice(suggestions)
			self.store_suggestion(who, arg)
			return random_sug
			
	def remove_lyrics(self, sug):
		filtered_list = []
		for s in sug:
			if s[0].find('lyrics') > -1: pass
			else: filtered_list.append(s[0])
		return filtered_list
	
	def store_suggestion(self, who, sug):
		sug = sug.strip('\r')
		sug = sug.strip()
		
		try:
			self.dong.db.insert('suggest', {'user': who, 'suggestion': sug})
		except:
			# UNIQUE constraint will balk here
			pass
		
	def pull_suggestion(self, callback, who, arg):
		"""Nudging the bot makes it return a random Google suggestion."""
		
		random_sug = self.dong.db.get_random_row('suggest')
		res = self.google_suggest(who, random_sug[2])
		return res

	
