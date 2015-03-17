from containers import *
import os
import midi, pprint
from collections import Counter

# const vars
NOTE_ON_EVENT = 144
NOTE_OFF_EVENT = 128
#test_template = {"E_fdim":[(4,7,10,1),.044],"G_fdim":[(7,10,1,4),.044],"Bb_fdim":[(10,1,4,7),.044],"Db_fdim":[(1,4,7,10),.044]}
all_templates = {
					"C_maj":[(0,4,7), .436],
					"C_dom7":[(0,4,7,10), .219],
					"C_min":[(0,3,7),.194],
					"C_fdim":[(0,3,6,9),.044],
					"C_hdim":[(0,3,6,10),.037],
					"C_dim":[(0,3,6),0.018],
					"Db_maj":[(1,5,8),.436],
					"Db_dom7":[(1,5,8,11), .219],
					"Db_min":[(1,4,8),.194],
					"Db_fdim":[(1,4,7,10),.044],
					"Db_hdim":[(1,4,7,11),.037],
					"Db_dim":[(1,4,7),0.018],
					"D_maj":[(2,6,9),.436],
					"D_dom7":[(2,6,9,0), .219],
					"D_min":[(2,5,9),.194],
					"D_fdim":[(2,5,8,11),.044],
					"D_hdim":[(2,5,8,0),.037],
					"D_dim":[(2,5,8),0.018],
					"Eb_maj":[(3,7,10),.436],
					"Eb_dom7":[(3,7,10,1), .219],
					"Eb_min":[(3,6,10),.194],
					"Eb_fdim":[(3,6,9,0),.044],
					"Eb_hdim":[(3,6,9,1),.037],
					"Eb_dim":[(3,6,9),0.018],
					"E_maj":[(4,8,11),.436],
					"E_dom7":[(4,8,11,2), .219],
					"E_min":[(4,7,11),.194],
					"E_fdim":[(4,7,10,1),.044],
					"E_hdim":[(4,7,10,2),.037],
					"E_dim":[(4,7,10),0.018],
					"F_maj":[(5,9,0),.436],
					"F_dom7":[(5,9,0,3), .219],
					"F_min":[(5,8,0),.194],
					"F_fdim":[(5,8,11,2),.044],
					"F_hdim":[(5,8,11,3),.037],
					"F_dim":[(5,8,11),0.018],
					"F#_maj":[(6,10,1),.436],
					"F#_dom7":[(6,10,1,4), .219],
					"F#_min":[(6,9,1),.194],
					"F#_fdim":[(6,9,0,3),.044],
					"F#_hdim":[(6,9,0,4),.037],
					"F#_dim":[(6,9,0),0.018],
					"G_maj":[(7,11,2),.436],
					"G_dom7":[(7,11,2,5), .219],
					"G_min":[(7,10,2),.194],
					"G_fdim":[(7,10,1,4),.044],
					"G_hdim":[(7,10,1,5),.037],
					"G_dim":[(7,10,1),0.018],
					"Ab_maj":[(8,0,3),.436],
					"Ab_dom7":[(8,0,3,6), .219],
					"Ab_min":[(8,11,3),.194],
					"Ab_fdim":[(8,11,2,5),.044],
					"Ab_hdim":[(8,11,2,6),.037],
					"Ab_dim":[(8,11,2),0.018],
					"A_maj":[(9,1,4),.436],
					"A_dom7":[(9,1,4,7), .219],
					"A_min":[(9,0,4),.194],
					"A_fdim":[(9,0,3,6),.044],
					"A_hdim":[(9,0,3,7),.037],
					"A_dim":[(9,0,3),0.018],
					"Bb_maj":[(10,2,5),.436],
					"Bb_dom7":[(10,2,5,8), .219],
					"Bb_min":[(10,1,5),.194],
					"Bb_fdim":[(10,1,4,7),.044],
					"Bb_hdim":[(10,1,4,8),.037],
					"Bb_dim":[(10,1,4),0.018],
					"B_maj":[(11,3,6),.436],
					"B_dom7":[(11,3,6,9), .219],
					"B_min":[(11,2,6),.194],
					"B_fdim":[(11,2,5,8),.044],
					"B_hdim":[(11,2,5,9),.037],
					"B_dim":[(11,2,5),0.018],	
				}

def read_midi_files(path):
	pattern = midi.read_midifile(path)
	pattern.make_ticks_abs()
	wanted_events = []
	# temp change back to pattern[0] later
	for event in pattern[0]:
		if event.statusmsg == NOTE_ON_EVENT or event.statusmsg == NOTE_OFF_EVENT:
			wanted_events.append(event)
	return wanted_events

# this code works
def find_minimal_segments(events):
	#pprint.pprint(events)
	node_array = []
	# temp change back to curr_tick = 0 later
	curr_tick = 0
	partition = MinimalSegment(curr_tick, [])
	count = 0

	for event in events:
		if event.tick == curr_tick:
			partition.addEvent(event)
		else:
			node_array.append(partition)
			curr_tick = event.tick
			partition = MinimalSegment(curr_tick,[])

			# add event to new partition
			partition.addEvent(event)

	# add very last partition
	node_array.append(partition)
	return node_array

# this code works
def score_edges(edge_matrix,node_array):
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

				# holds the weights of a note for a minimal segment
				weights = Counter({})
				for note in node_array[i].events:
					if note[1] !=0:
						# velocity isn't 0
						weights[note[0]] = 1
				note_weights += weights

			max_score = float("-inf")
			max_chord_name = ""

			# key, value of all_templates
			
			for chord,base in all_templates.iteritems():
				P = 0
				N = sum(note_weights.values())
				M = 0 

				# iterate through value tuple
				# for note in base[0]:
				for note in note_weights.keys():
					if note%12 in base[0]:
						P += note_weights[note]
						N -= note_weights[note]

				notes = [x%12 for x in note_weights.keys()]

				for note in base[0]:
					if note in notes:
						pass
					else:
						M+=1

				if max_score < (P - (M+N)):
					# new max template
					max_score = P - (M+N)
					max_chord_name = chord

				elif max_score == (P - (M+N)):
					# tie using Root Weight

					old_root = all_templates[max_chord_name][0][0]
					new_root = all_templates[chord][0][0]

					weight_of_old = 0
					weight_of_new = 0
					for x in notes:
						if x % 12 == old_root:
							weight_of_old += 1
						elif x % 12 == new_root:
							weight_of_new +=1

					if weight_of_old < weight_of_new:
						max_score = P - (M+N)
						max_chord_name = chord

					elif weight_of_new == weight_of_old:

						# tie, use highest probability
						max_score = max_score if all_templates[max_chord_name][1] > base[1] else P - (M + N)
						max_chord_name = max_chord_name if all_templates[max_chord_name][1] > base[1] else chord
			edge_matrix[row][col] = Edge(max_chord_name, max_score)

# this code works
def find_longest_path(start, end, graph):

	n = len(graph)
	LOWDIST=float("-inf")
	dist = dict((x, LOWDIST) for x in xrange(0,n))
	dist[start[0]] = 0
	comesfrom = dict()
	for row in xrange(0,n): #u
		for col in  xrange(row+1,n): #v
		#if dist(v) < dist(u) + score of (u,v)
			if dist[col] < (dist[row] + graph[row][col].score):
				dist[col] = dist[row] + graph[row][col].score
				comesfrom[col] = row

	maxpath = [end[1]]
	while maxpath[-1] != start[0]:
		maxpath.append(comesfrom[maxpath[-1]])
	maxpath.reverse()
	for i in range(0, len(maxpath)-1):
		val = (maxpath[i],maxpath[i+1])
		maxpath[i] = val
	maxpath.pop()
	return maxpath

# this code works:
def test_longest_path():
	size = 6
	test = [[Edge("",float("-inf")) for i in range(size)] for i in range(size)]
	test[0][1] = Edge("",5) 
	test[0][2] = Edge("",3) 
	test[1][3] = Edge("",6) 
	test[1][2] = Edge("",2) 
	test[2][4] = Edge("",4) 
	test[2][5] = Edge("",2) 
	test[2][3] = Edge("",7) 
	test[3][5] = Edge("",1) 
	test[3][4] = Edge("",-1) 
	test[4][5] = Edge("",-2) 
	print findLongestPath((0,1), (4,5), test)

def main():
	path = "kpcorpus/ex10a.mid"
	events = read_midi_files(path)
	node_array = find_minimal_segments(events)

	# make edge matrix
	size = len(node_array)
	edge_matrix = edge_matrix = [[float("-inf") for i in range(size)] for i in range(size)]

	score_edges(edge_matrix,node_array)

	# print the dag
	#for i in xrange(size):
		# for j in xrange(size):
		# 	try:
		# 		print edge_matrix[i][j].chord_name
		# 		print edge_matrix[i][j].score
		# 	except:
		# 		print "INF"
		# print "========================================="

	n = len(edge_matrix)
	maxpath = find_longest_path((0,1),(n-2,n-1),edge_matrix)

	# remove repeated chord_names
	prev_edge = None
	for index, edge in enumerate(maxpath):
		curr_edge = edge_matrix[edge[0]][edge[1]]
		try:
			if curr_edge.chord_name == prev_edge.chord_name:
				maxpath[index - 1] = None
		except:
			pass
		prev_edge = curr_edge

	# print out the longest path
	for edge in maxpath:
		if edge is not None:
			print edge_matrix[edge[0]][edge[1]].chord_name
			print node_array[edge[1]].tick

main()
