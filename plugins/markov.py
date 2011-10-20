
import re
import random
from time import time

from plugin import Plugin

class Markov(Plugin):
	""" Markov Chain plugin, inspired by the example here:
		http://www.evanfosmark.com/2009/11/python-markov-chains-and-how-to-use-them/
		Simplified for my case, did not need defaultdicts and I wanted more randomization.
	"""

	class START(object):pass
	class END(object):pass

	def __init__(self, name, dong):
		super(Markov, self).__init__(name, dong)

		self.wordpat = re.compile('.*?([a-zA-Z0-9\'\-]+).*?')
		self.texts = self.conf['texts']
		self.chains = {}
		self.process_all_texts()

	def add(self, chain, iterable):
		"""	Since large texts can come in all sort of formats and be quite ugly to parse
			(ex. the Bible, with all its chapter numbers), I prefer using a pure "word"
			regexp instead of doing .split().
		"""
		
		item1 = item2 = self.START
		
		for item3 in iterable:
			s = re.search(self.wordpat, item3)
			if s:
				item3 = s.group(1)

				self.chains[chain].setdefault((item1, item2), []).append(item3)

				item1 = item2
				item2 = item3

		self.chains[chain].setdefault((item1, item2), []).append(self.END)
		
	def random_output(self, chain, max=20):
		output = []

		# Randomize starting words
		item1, item2 = random.choice(self.chains[chain].keys())

		for i in range(max-2):
			item3 = random.choice(self.chains[chain][(item1, item2)])
			if item3 is self.END:
				break

			item1 = item2
			item2 = item3

			output.append(item3)
		return output
	
	def process_all_texts(self):
		for name,file in self.texts.items():
			now = time.time()
			self.add_body(name, file)
			then = time.time()
			print "Processed %s (%s items) in %s seconds." % (name, len(self.chains[name]), str(int(then - now)))

	def add_body(self, name, file):
		self.chains[name] = {}
		full = open(file).read()
		words = full.split(' ')
		self.add(name, words)
