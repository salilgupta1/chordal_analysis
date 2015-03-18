from containers import *
import midi, pprint, re, os
from collections import Counter
import scipy.spatial.distance as e

# const vars
NOTE_ON_EVENT = 144
NOTE_OFF_EVENT = 128
LYRIC_EVENT = 5
MIN_SEGMENT_LENGTH  = 60
PENALTY = .25
EXTRAS = {
	
}
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
SCORING = {
	"C#_min":[(1,4,8),.194],
	"C#_dom7":[(1,5,8,11), .219],
	"C#_hdim":[(1,4,7,11),.037],
	"G#_dim":[(8,11,2),0.018],
	"G#_hdim":[(8,11,2,6),.037],
	"A#_dim":[(10,1,4),0.018],
}

SCORING.update(all_templates)

def read_midi_files(path):
	pattern = midi.read_midifile(path)
	pattern.make_ticks_abs()
	wanted_events = []
	answer_key = []

	# pull wanted events and answer_key
	for event in pattern[0]:
		if event.statusmsg == NOTE_ON_EVENT or event.statusmsg == NOTE_OFF_EVENT:
			wanted_events.append(event)
		try:
			if event.metacommand == LYRIC_EVENT:
				text = re.sub(r'_\d+',"",event.text)
				text = re.sub(r'maj(_)?\d+',"maj",text)
				text = re.sub(r'min(_)?\d+',"min",text)
				answer_key.append([event.tick, text.rstrip()])

		except AttributeError:
			pass

	# format answer_key
	for i, key in enumerate(answer_key):
		if i is not 0 and key[1] == answer_key[i - 1][1]:
			del answer_key[i - 1]

	n = len(answer_key) - 1 

	for i, key in enumerate(answer_key):
		if i < n:
			key[0] = answer_key[i+1][0]
		else:
			key[0] = wanted_events[-1].tick

	return (wanted_events, answer_key)

def find_minimal_segments(events):
	node_array = []
	curr_tick = events[0].tick
	partition = MinimalSegment(curr_tick, 0, [])

	last_tick = 0
	for event in events:
		last_tick = event.tick
		if event.tick == curr_tick:
			partition.addEvent(event)
		else:
			partition.end_tick = event.tick
			node_array.append(partition)
			curr_tick = event.tick
			partition = MinimalSegment(curr_tick, 0, [])
			partition.addEvent(event)

	partition.end_tick = last_tick
	node_array.append(partition)

	# for node in node_array:
	# 	pprint.pprint(node.events)
	# 	print node.tick
	# 	print node.end_tick
	# 	print "\n"
	return node_array

def score_edges(edge_matrix,node_array):

	# traverse edges in matrix
	n = len(edge_matrix)
	for row in xrange(n):
		for col in xrange(row+1,n):
			
			# holds note weights across all minimal segments in an edge
			note_weights = Counter({}) 
			bad_segments = 0
			for i in xrange(row, col+1):

				# holds the weights of a note for a single minimal segment
				weights = Counter({})

				segment_length = node_array[i].end_tick - node_array[i].tick

				# getting each event in a segment
				for note in node_array[i].events:
					if note[1] !=0:
						if segment_length > MIN_SEGMENT_LENGTH:
							weights[note[0]] = 1
						else:
							weights[note[0]] = PENALTY

				# aggregate weights of notes across minimal segments in edge
				note_weights += weights

			max_score = float("-inf")
			max_chord_name = ""
			
			# iterate through templates
			for chord,base in all_templates.iteritems():
				P = 0
				N = sum(note_weights.values())
				M = 0 

				# score edge-to-template similarity
				for note in note_weights.keys():
					if note%12 in base[0]:
						P += note_weights[note]
						N -= note_weights[note]

				notes = [x%12 for x in note_weights.keys()]

				for note in base[0]:
					if note not in notes:
						M+=1

				# update max score and best template for edge
				if max_score < (P - (M+N)):
					max_score = P - (M+N)
					max_chord_name = chord

				# tie
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
	print find_longest_path((0,1), (4,5), test)

def remove_repeat_chords(max_path, edge_matrix):
	prev_edge = None
	for index, edge in enumerate(max_path):
		curr_edge = edge_matrix[edge[0]][edge[1]]
		try:
			if curr_edge.chord_name == prev_edge.chord_name:
				max_path[index - 1] = None
		except:
			pass
		prev_edge = curr_edge

def evaluate(results, answer_key):
	# evaluate 
	final_score = 0
	for result in results:
		time_measures = []
		chord_measures = []
		max_time = float("-inf")
		min_time = float("inf")

		max_chord = float("-inf")
		min_chord = float("inf")

		error = False
		try:
			for key in answer_key:
				# calculate distance
				time_measure = abs(result[0] - key[0])
				max_time = max(max_time, time_measure)
				min_time = min(min_time, time_measure)
				
				chord_measure = euclidean_distance(SCORING[result[1]][0], SCORING[key[1]][0])

				max_chord = max(max_chord, chord_measure)
				min_chord = min(min_chord, chord_measure)

				time_measures.append(time_measure)
				chord_measures.append(chord_measure)
		except KeyError:
			error = True
			EXTRAS[key[1]] = 1

		if error:
			return None

		# normalize data to between 0 and 10
		chord_measures = normalize(min_chord, max_chord, chord_measures)
		time_measures = normalize(min_time, max_time, time_measures)

		# add penalties together
		penalties = [sum(x) for x in zip(chord_measures, time_measures)] 
		# get min penalty
		min_pen = float("inf")
		min_index = 0
		for index, pen in enumerate(penalties):
			if pen < min_pen:
				min_pen = pen
				min_index = index
			elif pen == min_pen:
				# if tie then get one with min time measure
				if time_measures[index] < time_measures[min_index]:
					min_pen = pen
					min_index = index
		final_score += min_pen
	# average penalities
	final_score /= len(results)
	final_score = 5 - final_score

	return final_score

	# get the min "penalty" and subtract from 10

def normalize(mini, maxi, data):
	norm_data = []
	for d in data:
		norm = abs(d - mini)*10/abs(maxi - mini)
		norm_data.append(norm)
	return norm_data

def euclidean_distance(x,y):
	len_x = len(x)
	len_y = len(y)

	if len_x > len_y:
		y = list(y)
		y.append(-100)
	elif len_y > len_x:
		x = list(x)
		x.append(-100)

	return e.euclidean(x,y)

def main():
	files = next(os.walk("kpcorpus"))[2]
	print len(files)
	files.remove(".DS_Store")
	for f in files[20:30]:
		(events, answer_key) = read_midi_files("kpcorpus/%s" % f)
		node_array = find_minimal_segments(events)

		size = len(node_array)
		edge_matrix = edge_matrix = [[float("-inf") for i in range(size)] for i in range(size)]

		score_edges(edge_matrix,node_array)

		max_path = find_longest_path((0,1), (size-2,size-1), edge_matrix)

		# remove repeated chord_names
		remove_repeat_chords(max_path, edge_matrix)

		result = []

		for edge in max_path:
			if edge is not None:
				result.append([node_array[edge[1]].tick, edge_matrix[edge[0]][edge[1]].chord_name])

		# it don't work :(
		score = evaluate(result, answer_key)
		print f, score

	print EXTRAS
main()