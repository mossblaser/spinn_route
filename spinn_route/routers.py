#!/usr/bin/env python

"""
Implementations of various routing algorithms. The routing algorithms feature
the following interface::
	
	example(source_core, sink_cores, chips) --> ([node_sequence, ...], unrouted_sinks)

Where:
* source_core is the Core where the route begins
* sink_cores is a list of destinations for the route
* chips is a list of (Router, [Core,...]) tuples which define the network
  within which to route.

Returns a two values:
* A list of sequences of nodes which represent the route. Each sequence
  starts with the source core and ends with a sink core. These routes are not
  guaranteed to be possible.
* A list of sinks to which the algorithm was unable to route (e.g. due to link
  failures).
"""

import operator

import model
import topology


def dimension_order_route(source, sinks, chips, use_wrap_around = False, dimension_order=(0,1,2)):
	"""
	Simple, naive dimension order routing optionally supporting wrap-around links.
	Note that when two DOR routes exist of equivalent length, one will be chosen
	at random.
	
	This routing algorithm does not attempt to route around dead links/cores and
	so some routes may fail in the presence of network errors.
	"""
	
	# Calculate the bounds of the system's size (in case wrap_around is used)
	width  = max(x for (x,y) in chips.iterkeys()) + 1
	height = max(y for (x,y) in chips.iterkeys()) + 1
	
	node_sequences = []
	unrouted_sinks = []
	
	for sink in sinks:
		source_pos = model.core_to_router(source).position
		sink_pos   = model.core_to_router(sink).position
		
		# Find the shortest vector from the source to the sink
		if use_wrap_around:
			vector = list(topology.to_torus_shortest_path(source_pos, sink_pos, (width,height)))
		else:
			vector = list(topology.to_shortest_path(topology.to_xyz(map( operator.sub
			                                                           , sink_pos
			                                                           , source_pos
			                                                           ))))
		
		node_sequence = [source, model.core_to_router(source)]
		
		# Route down each dimension in the given order
		for dimension in dimension_order:
			while vector[dimension] != 0:
				vx,vy = topology.to_xy((int(dimension == 0), int(dimension == 1), int(dimension == 2)))
				x, y  = node_sequence[-1].position
				
				if vector[dimension] > 0:
					x += vx
					y += vy
					vector[dimension] -= 1
				else:
					x -= vx
					y -= vy
					vector[dimension] += 1
				
				x %= width
				y %= height
				
				node_sequence.append(chips[(x,y)].router)
		
		# Add the sink
		node_sequence.append(sink)
		
		# Add the route
		if model.is_path_connected(node_sequence):
			node_sequences.append(node_sequence)
		else:
			unrouted_sinks.append(sink)
	
	return node_sequences, unrouted_sinks
