
class MinimalSegment():
	def __init__(self, tick, events=[]):
		self.tick = tick
		self.events = events # [(pitch,velocity)] list of tuples

	def addEvent(self,event):
		data_tuple = (event.data[0], event.data[1])
		self.events.append(data_tuple)


class Edge():
	def __init__(self, chord_name, score):
		self.chord_name = chord_name
		self.score = score

