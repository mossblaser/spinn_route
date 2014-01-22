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



