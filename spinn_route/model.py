#!/usr/bin/env python

"""
Components of a model of a SpiNNaker network consisting of interconnected cores
and routers with multicast routes mapped out within it.
"""

import topology


class Route(object):
	"""
	A specific multicast route with a single sender and arbitary number of
	receivers. Essentially corresponds to a specific SpiNNaker routing key.
	"""
	
	def __init__(self, key):
		self.key = key
	
	def __repr__(self):
		return "Route(%s)"%(repr(self.key))


class Node(object):
	"""
	A node is an element in the SpiNNaker network. It can accept and produce
	packets.
	"""
	
	def __init__(self, ports):
		"""
		Takes a list of port identifiers and sets those ports to disconnected.
		"""
		
		# A set of (bidirectional) links of the form {Port: Node}.
		self.connections = {}
		for port in ports:
			self.connections[port] = None
	
	
	def connect(self, port, other, other_port):
		"""
		Connect this node to another node via the given ports.
		"""
		# Check that no connection has already been set up.
		assert(self.connections[port] is None)
		assert(other.connections[other_port] is None)
		
		self.connections[port] = other
		other.connections[other_port] = self
	
	
	def disconnect(self, port):
		"""
		Disconnect a given port.
		"""
		# Check that the specified connection exists
		assert(self.connections[port] is not None)
		other = self.connections[port]
		
		# Find the port at the other end of the connection (and check it is
		# connected)
		for other_port, other_ in other.connections.iteritems():
			if other_ == self:
				break
		assert(other.connections[other_port] == self)
		
		self.connections[port] = None
		other.connections[other_port] = None


class Core(Node):
	"""
	A Core in a single chip in a SpiNNaker system.
	"""
	
	# Identifier for a core's connection to the network via its local router.
	NETWORK_PORT = object()
	
	def __init__(self, core_id):
		Node.__init__(self, [Core.NETWORK_PORT])
		
		# The ID number assigned to the given core
		self.core_id = core_id
		
		# The set of Routes sourced at this core
		self.sources = set()
		
		# The set of Routes sinked at this core
		self.sinks = set()
	
	
	def __repr__(self):
		return "Core(%s)<->%s"%(repr(self.core_id), repr(self.connections[Core.NETWORK_PORT]))



class Router(Node):
	"""
	The router in a SpiNNaker chip.
	"""
	
	# Router network ports
	INTERNAL_PORTS = [object() for _ in range(18)]
	EXTERNAL_PORTS = [ topology.EAST
	                 , topology.NORTH_EAST
	                 , topology.NORTH
	                 , topology.WEST
	                 , topology.SOUTH_WEST
	                 , topology.SOUTH
	                 ]
	
	def __init__(self, position, board):
		"""
		position is the (x,y) coordinate of the node in the network.
		
		board is the (x,y) coordinate of the board the router is on.
		"""
		Node.__init__(self, Router.INTERNAL_PORTS + Router.EXTERNAL_PORTS)
		
		# The logical position of the router (chip) in the network.
		self.position = position
		
		# A dictionary of routes flowing through the router of the form:
		# {Route: (incoming_port, set(outgoing_ports)), ...}.
		self.routes = {}
	
	
	def __repr__(self):
		return "Router(%s)"%(repr(self.position))



def core_to_router(core):
	"""
	Given a core, return the associated router.
	"""
	return core.connections[Core.NETWORK_PORT]


def make_chip(chip_position = (0,0), chip_board = (0,0), num_cores = 18):
	"""
	Create a single, multi-core SpiNNaker chip. Returns a tuple (router, [cores]).
	"""
	assert(num_cores <= len(Router.INTERNAL_PORTS))
	
	# Create the router and cores
	router = Router(chip_position, chip_board)
	cores = [Core(core_id) for core_id in range(num_cores)]
	
	# Connect everything up
	for core_id in range(num_cores):
		router.connect( Router.INTERNAL_PORTS[core_id]
		              , cores[core_id], Core.NETWORK_PORT
		              )
	
	return (router, cores)


def fully_connect_chips(chips, wrap_around = False):
	"""
	Given a set of chips (i.e. (router, cores) tuples), fully interconnects the
	chips optionally including wrap-around links.
	"""
	# Calculate the bounds of the system's size (in case wrap_around is used)
	width  = max(x for (x,y) in chips.iterkeys()) + 1
	height = max(y for (x,y) in chips.iterkeys()) + 1
	
	# Connect up the nodes to their neighbours
	for position, (router, cores) in chips.iteritems():
		for direction in [topology.EAST, topology.NORTH_EAST, topology.NORTH]:
			next_x, next_y = topology.to_xy(
				topology.add_direction(topology.to_xyz(position), direction))
			
			if wrap_around:
				next_x %= width
				next_y %= height
			
			# Only connect up to nodes which actually exist...
			if (next_x, next_y) in chips:
				router.connect(direction, chips[(next_x, next_y)][0], topology.opposite(direction))


def make_rectangular_board(width = 2, height = 2, wrap_around = False, board = (0,0), num_cores = 18):
	"""
	Produce a system containing a rectangular system of chips (optionally with
	wrap-around links) of a given width and height. Defaults to a 2x2 board (like
	the SpiNN-3 "Bunnie Bot" boards). Returns a dict {(x,y): (router, cores),
	...}.
	"""
	
	chips = {}
	
	for y in range(height):
		for x in range(width):
			chips[(x,y)] = make_chip((x,y), board, num_cores)
	
	fully_connect_chips(chips, wrap_around = wrap_around)
	
	return chips


def make_hexagonal_board(layers = 4, board = (0,0), num_cores = 18):
	"""
	Produce a system containing a hexagonal system of chips (without wrap-around
	links) of a given number of layers. Defaults to a 4-layer (48 chip) board
	(like the SpiNN-4/SpiNN-5 boards). Returns a dict {(x,y): (router, cores),
	...}.
	"""
	
	chips = {}
	
	for position in topology.hexagon(layers):
		chips[position] = make_chip(position, board, num_cores)
	
	fully_connect_chips(chips)
	
	return chips


def make_multi_board_torus(width = 1, height = 1, layers = 4, num_cores = 18):
	"""
	Produce a system containing multiple boards arranged as a given number of
	"threeboards" wide and high arrangement of of boards with the given number of
	layers. Defaults to a single threeboard system of 48-node boards with 18
	cores. Returns a dict {(x,y): (router, cores), ...}.
	"""
	
	chips = {}
	
	width_nodes  = width*12
	height_nodes = height*12
	
	for (board_x, board_y, board_z) in topology.threeboards(width, height):
		assert(board_z == 0)
		for (x,y) in topology.hexagon(layers):
			x += (board_x*4 ) + (board_y*4)
			y += (board_x*-4) + (board_y*8)
			
			x %= width_nodes
			y %= height_nodes
			
			chips[(x,y)] = make_chip((x,y), (board_x,board_y), num_cores)
	
	fully_connect_chips(chips, wrap_around = True)
	
	return chips


def get_all_routes(chips):
	"""
	Given a set of chips (i.e. a dict {(x,y):(router, [cores]),...}), return a
	dictionary {Route: (source_core, [sink_cores]), ...}.
	"""
	
	routes = {}
	
	# Find all the routes (and sources)
	for router, cores in chips.itervalues():
		for core in cores:
			for route in core.sources:
				assert(route not in routes)
				routes[route] = (core, set())
	
	# Fill in the sinks
	for router, cores in chips.itervalues():
		for core in cores:
			for route in core.sinks:
				routes[route][1].add(core)
	
	return routes


def is_path_connected(node_sequence):
	"""
	Given a sequence of Nodes (i.e. Cores and Routers), test whether it is
	possible to route a packet in exactly this sequence.
	"""
	
	i1 = iter(node_sequence)
	i2 = iter(node_sequence)
	i2.next()
	
	for node, next_node in zip(i1, i2):
		if next_node not in node.connections.itervalues():
			return False
	return True


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
			if connection == node:
				return port
		
		raise Exception(("No connection exists between %s and %s " +
		                 "and so no route can be created directly between them!")%(
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
