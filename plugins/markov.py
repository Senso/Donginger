
import collections
import random

from plugin import Plugin

class Markov(Plugin, collections.defaultdict):
	"""	Markov Chain plugin, taken from
		http://www.evanfosmark.com/2009/11/python-markov-chains-and-how-to-use-them/
	"""
	
	class START(object):pass
	class END(object):pass
	
	def __init__(self, name, dong):
		super(Markov, self).__init__(name, dong)
		collections.defaultdict.__init__(self, DynamicDie)
		
		self.texts = self.conf['texts']
		self.chains = {}
		self.process_all_texts()
		
	def add(self, chain, iterable):
		""" Insert an iterable (pattern) item into the markov chain.
			The order of the pattern will define more of the chain.
		"""
		item1 = item2 = Markov.START
		for item3 in iterable:
			self.chains[chain][(item1, item2)].add_side(item3)
			item1 = item2
			item2 = item3
		self.chains[chain][(item1, item2)].add_side(Markov.END)

	def random_output(self, chain, max=100):
		""" Generate a list of elements from the markov chain.
			The `max` value is in place in order to prevent excessive iteration.
		"""
		output = []
		item1 = item2 = Markov.START
		for i in range(max-2):
			item3 = self.chains[chain][(item1, item2)].roll()
			if item3 is Markov.END:
				break
			output.append(item3)
			item1 = item2
			item2 = item3
		return output
	
	def process_all_texts(self):
		for name,file in self.texts.items:
			self.add_body(name, file)
	
	def add_body(self, name, file):
		self.chains[name] = {}
		for line in file:
			line = line.split()
			for word in line:
				word = word.strip()
				if word:
					self.add(name, word)
		
		
class DynamicDie(collections.defaultdict):

	def __init__(self):
		collections.defaultdict.__init__(self, int)

	def add_side(self, side):
		self[side] += 1

	def total_sides(self):
		return sum(self.values())

	def roll(self):
		random_num = random.randint(0, self.total_sides())
		total_pos = 0
		for side, qty in self.items():
			total_pos += qty
			if random_num <= total_pos:
				return side