#!/usr/bin/env python

"""
Utlity functions for assembling networks.
"""

import model
import topology


def make_chip(chip_position = (0,0), chip_board = (0,0), num_cores = 18):
	"""
	Create a single, multi-core SpiNNaker chip. Returns a tuple (router, [cores]).
	"""
	assert(num_cores <= len(model.Router.INTERNAL_PORTS))
	
	# Create the router and cores
	router = model.Router(chip_position, chip_board)
	cores = [model.Core(core_id) for core_id in range(num_cores)]
	
	# Connect everything up
	for core_id in range(num_cores):
		router.connect( model.Router.INTERNAL_PORTS[core_id]
		              , cores[core_id], model.Core.NETWORK_PORT
		              )
	
	return (router, cores)


def fully_connect_chips(chips, wrap_around = False):
	"""
	Given a set of chips (i.e. (router, cores) tuples), fully interconnects the
	chips optionally including wrap-around links.
	"""
	# Generate a look-up from position to router.
	routers = {}
	for router, cores in chips:
		routers[router.position] = router
	
	# Calculate the bounds of the system's size (in case wrap_around is used)
	width  = max(x for (x,y) in routers.iterkeys()) + 1
	height = max(y for (x,y) in routers.iterkeys()) + 1
	
	# Connect up the nodes to their neighbours
	for position, router in routers.iteritems():
		for direction in [topology.EAST, topology.NORTH_EAST, topology.NORTH]:
			next_x, next_y = topology.to_xy(
				topology.add_direction(topology.to_xyz(position), direction))
			
			if wrap_around:
				next_x %= width
				next_y %= height
			
			# Only connect up to nodes which actually exist...
			if (next_x, next_y) in routers:
				router.connect(direction, routers[(next_x, next_y)], topology.opposite(direction))


def make_rectangular_board(width = 2, height = 2, board = (0,0), num_cores = 18):
	"""
	Produce a system containing a rectangular system of chips (without wrap-around
	links) of a given width and height. Defaults to a 2x2 board (like the SpiNN-3
	"Bunnie Bot" boards).
	"""
	
	chips = []
	
	for y in range(height):
		for x in range(width):
			chips.append(make_chip((x,y), board, num_cores))
	
	fully_connect_chips(chips)
	
	return chips


def make_hexagonal_board(layers = 4, board = (0,0), num_cores = 18):
	"""
	Produce a system containing a hexagonal system of chips (without wrap-around
	links) of a given number of layers. Defaults to a 4-layer (48 chip) board
	(like the SpiNN-4/SpiNN-5 boards).
	"""
	
	chips = []
	
	for position in topology.hexagon(layers):
		chips.append(make_chip(position, board, num_cores))
	
	fully_connect_chips(chips)
	
	return chips


def make_multi_board_torus(width = 1, height = 1, layers = 4, num_cores = 18):
	"""
	Produce a system containing multiple boards arranged as a given number of
	"threeboards" wide and high arrangement of of boards with the given number of
	layers. Defaults to a single threeboard system of 48-node boards with 18 cores.
	"""
	
	chips = []
	
	width_nodes  = width*12
	height_nodes = height*12
	
	for (board_x, board_y, board_z) in topology.threeboards(width, height):
		assert(board_z == 0)
		for (x,y) in topology.hexagon(layers):
			x += (board_x*4 ) + (board_y*4)
			y += (board_x*-4) + (board_y*8)
			
			x %= width_nodes
			y %= height_nodes
			
			chips.append(make_chip((x,y), (board_x,board_y), num_cores))
	
	fully_connect_chips(chips, wrap_around = True)
	
	return chips


def get_all_routes(chips):
	"""
	Given a set of chips (i.e. (router, [cores]) tuples), return a dictionary
	{Route: (source_core, [sink_cores]), ...}.
	"""
	
	routes = {}
	
	# Find all the routes (and sources)
	for (router, cores) in chips:
		for core in cores:
			for route in core.sources:
				assert(route not in routes)
				routes[route] = (core, set())
	
	# Fill in the sinks
	for (router, cores) in chips:
		for core in cores:
			for route in core.sinks:
				routes[route][1].add(core)
	
	return routes


def add_route(route, node_sequence):
	r"""
	Given a sequence of Nodes of the form [Core, Router, Router, ..., Core], fill
	in the routing table entries in the routers involved and also the route
	source/sink entries in the Cores in order to facilitate connectivity between
	the nodes. The sequence must be between a series of connected Cores/Routers
	from exactly one source Core to one sink Core.
	
	This means that to connect a multicast route, this function must be called
	multiple times for each branch. For example, to connect the following:
		
		            ,---> C --> D
		           /
		A --> B --<
		           \
		            `---> E --> F
	
	The function should be called twice such as::
		
		add_router_entries(route, [A, B, C, D])
		add_router_entries(route, [A, B, E, F])
	"""
	
	# Produce a sliding window which iterates over the sequence showing the
	# predecessor and successor to each router.
	ts0 = iter(node_sequence)
	ts1 = iter(node_sequence)
	ts1.next()
	ts2 = iter(node_sequence)
	ts2.next()
	ts2.next()
	sliding_window = zip(ts0, ts1, ts2)
	
	def get_port(router, node):
		"""
		Return the port identifier for the port connecting the given router to the
		given node. If no port connects to this node, throw an Exception.
		"""
		for port, connection in router.connections.iteritems():
			if connection is not None and connection[0] == node:
				return port
		
		raise Exception("No connection exists between %s and %s " +
		                "and so no route can be created directly between them!"%(
		                  repr(router), repr(node)
		                ))
		
	
	# Add router entries
	for prev_node, router, next_node in sliding_window:
		if route not in router.routes:
			router.routes[route] = (
				# Incoming port
				get_port(router, prev_node),
				# Outgoing port
				[get_port(router, next_node)]
			)
		else:
			# This route already passes through this node, it may fork here or remain
			# the same.
			
			# Check that the route only ever enters in one direction (otherwise it
			# does not form a tree which all 1:N multicast routes must).
			assert(router.routes[route][0] == get_port(router, prev_node))
			
			outgoing_port = get_port(router, next_node)
			if outgoing_port not in router.routes[route][1]:
				router.routes[route][1].append(outgoing_port)
	
	# Add core source/sink entries
	node_sequence[0].sources.add(route)
	node_sequence[-1].sinks.add(route)
