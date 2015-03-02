from containers import *
import os
import midi
from collections import Counter

# global vars
node_array = []
edge_matrix = None

# const vars
NOTE_ON_EVENT = 144
NOTE_OFF_EVENT = 128

base_templates = {"Major Triad":[(0,4,7), .436],
					"Dom 7":[(0,4,7,10), .219],
					"Minor Triad":[(0,3,7),.194],
					"Fully Diminished 7th":[(0,3,6,9),.044],
					"Half Diminished 7th":[(0,3,6,10),.037],
					"Diminished Triad":[(0,3,6),0.018]
				}

def read_midi_files(path):
	pattern = midi.read_midifile(path)
	pattern.make_ticks_abs()
	wanted_events = []
	for event in pattern[0]:
		if event.statusmsg == NOTE_OFF_EVENT or event.statusmsg == NOTE_ON_EVENT:
			wanted_events.append(event)

	return wanted_events

def find_minimal_segments(events):
	curr_tick = 0
	partition = MinimalSegment(curr_tick, [])
	for event in events:
		if event.tick == curr_tick:
			partition.addEvent(event)
		else:
			node_array.append(partition)
			curr_tick = event.tick
			partition = MinimalSegment(curr_tick,[])

def create_edge_matrix():
	size = len(node_array)
	global edge_matrix
	edge_matrix = [[float("-inf") for i in range(size)] for i in range(size)]


def score_edges():
	# traverse edge matrix
	# at each point score the edge and store chord name
	n = len(edge_matrix)
	for row in xrange(n):
		for col in xrange(row+1,n):
			
			# now we are scoring an edge
			# holds note weights across all minimal segments in an edge
			note_weights = Counter({}) 
			for i in xrange(row, col+1):
				# getting each minimal segment
				# inside an edge

				# holds the weights of a note for a minimal segment
				weights = Counter({})
				for note in node_array[i].events:
					if note[1] !=0:
						# velocity isn't 0
						weights[note[0]%12] = 1
				note_weights += weights

			score = float("-inf")
			chord_name = ""
			# key, value of base_templates
			for chord,base in base_templates.iteritems():
				P = 0
				N = sum(note_weights.values())
				M = 0 

				# iterate through value tuple
				for note in base[0]:
					try:
						P += note_weights[note]
						N -= note_weights[note]
					except KeyError:
						M +=1
				if score < (P - (M+N)):
					# new max template
					score = P - (M+N)
					chord_name = chord
				elif score == (P - (M+N)):
					# tie, use highest probability
					score = score if base_templates[chord_name][1] > base[1] else P - (M + N)
					chord_name = chord_name if base_templates[chord_name][1] > base[1] else chord
			edge_matrix[row][col] = Edge(chord_name, score)
	print edge_matrix[0][3].chord_name
	print edge_matrix[0][3].score

def findLongestPath():
	pass

def create_chord_name():
	pass

def main():
	path = "kpcorpus/ex1a.mid"
	events = read_midi_files(path)
	find_minimal_segments(events)

	create_edge_matrix()
	score_edges()

main()
