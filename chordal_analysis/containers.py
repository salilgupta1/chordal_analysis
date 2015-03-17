
class MinimalSegment():
	def __init__(self, tick,end_tick=0, events=[]):
		self.tick = tick
		self.events = events # [(pitch,velocity)] list of tuples
		self.end_tick = end_tick

	def addEvent(self,event):
		data_tuple = (event.data[0], event.data[1])
		self.events.append(data_tuple)


class Edge():
	def __init__(self, chord_name, score):
		self.chord_name = chord_name
		self.score = score

