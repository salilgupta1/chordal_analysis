from containers import *
import os
import midi
from collections import Counter
# Niki Patel
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

all_templates = {"C_MAJ":[(0,4,7), .436],
					"C_DOM_7":[(0,4,7,10), .219],
					"C_MIN":[(0,3,7),.194],
					"C_FD_7":[(0,3,6,9),.044],
					"C_HD_7":[(0,3,6,10),.037],
					"C_DIM":[(0,3,6),0.018],
					"C#_MAJ":[(1,5,8),.436],
					"C#_DOM_7":[(1,5,8,11), .219],
					"C#_MIN":[(1,4,8),.194],
					"C#_FD_7":[(1,4,7,10),.044],
					"C#_HD_7":[(1,4,7,11),.037],
					"C#_DIM":[(1,4,7),0.018],
					"D_MAJ":[(2,6,9),.436],
					"D_DOM_7":[(2,6,9,0), .219],
					"D_MIN":[(2,5,9),.194],
					"D_FD_7":[(2,5,8,11),.044],
					"D_HD_7":[(2,5,8,0),.037],
					"D_DIM":[(2,5,8),0.018],
					"D#_MAJ":[(3,7,10),.436],
					"D#_DOM_7":[(3,7,10,1), .219],
					"D#_MIN":[(3,6,10),.194],
					"D#_FD_7":[(3,6,9,0),.044],
					"D#_HD_7":[(3,6,9,1),.037],
					"D#_DIM":[(3,6,9),0.018],
					"E_MAJ":[(4,8,11),.436],
					"E_DOM_7":[(4,8,11,2), .219],
					"E_MIN":[(4,7,11),.194],
					"E_FD_7":[(4,7,10,1),.044],
					"E_HD_7":[(4,7,10,2),.037],
					"E_DIM":[(4,7,10),0.018],
					"F_MAJ":[(5,9,0),.436],
					"F_DOM_7":[(5,9,0,3), .219],
					"F_MIN":[(5,8,0),.194],
					"F_FD_7":[(5,8,11,2),.044],
					"F_HD_7":[(5,8,11,3),.037],
					"F_DIM":[(5,8,11),0.018],
					"F#_MAJ":[(6,10,1),.436],
					"F#_DOM_7":[(6,10,1,4), .219],
					"F#_MIN":[(6,9,1),.194],
					"F#_FD_7":[(6,9,0,3),.044],
					"F#_HD_7":[(6,9,0,4),.037],
					"F#_DIM":[(6,9,0),0.018],
					"G_MAJ":[(7,11,2),.436],
					"G_DOM_7":[(7,11,2,5), .219],
					"G_MIN":[(7,10,2),.194],
					"G_FD_7":[(7,10,1,4),.044],
					"G_HD_7":[(7,10,1,5),.037],
					"G_DIM":[(7,10,1),0.018],
					"G#_MAJ":[(8,0,3),.436],
					"G#_DOM_7":[(8,0,3,6), .219],
					"G#_MIN":[(8,11,3),.194],
					"G#_FD_7":[(8,11,2,5),.044],
					"G#_HD_7":[(8,11,2,6),.037],
					"G#_DIM":[(8,11,2),0.018],
					"A_MAJ":[(9,1,4),.436],
					"A_DOM_7":[(9,1,4,7), .219],
					"A_MIN":[(9,0,4),.194],
					"A_FD_7":[(9,0,3,6),.044],
					"A_HD_7":[(9,0,3,7),.037],
					"A_DIM":[(9,0,3),0.018],
					"A#_MAJ":[(10,2,5),.436],
					"A#_DOM_7":[(10,2,5,8), .219],
					"A#_MIN":[(10,1,5),.194],
					"A#_FD_7":[(10,1,4,7),.044],
					"A#_HD_7":[(10,1,4,8),.037],
					"A#_DIM":[(10,1,4),0.018],
					"B_MAJ":[(11,3,6),.436],
					"B_DOM_7":[(11,3,6,9), .219],
					"B_MIN":[(11,2,6),.194],
					"B_FD_7":[(11,2,5,8),.044],
					"B_HD_7":[(11,2,5,9),.037],
					"B_DIM":[(11,2,5),0.018],	
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
