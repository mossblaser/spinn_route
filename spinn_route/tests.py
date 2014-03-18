#!/usr/bin/env python

"""
Unit tests. Not comprehensive but just quick and dirty... Usage:

python tests.py
"""

import unittest
import pprint

import topology
import model
import routers
import table_gen

class TopologyTests(unittest.TestCase):
	"""
	Tests the topology utility functions
	"""
	
	def test_next(self):
		cw  = topology.next_cw
		ccw = topology.next_ccw
		
		# Clockwise
		self.assertEqual(cw(topology.EAST),       topology.SOUTH)
		self.assertEqual(cw(topology.NORTH_EAST), topology.EAST)
		self.assertEqual(cw(topology.NORTH),      topology.NORTH_EAST)
		self.assertEqual(cw(topology.WEST),       topology.NORTH)
		self.assertEqual(cw(topology.SOUTH_WEST), topology.WEST)
		self.assertEqual(cw(topology.SOUTH),      topology.SOUTH_WEST)
		
		# Counter-Clockwise
		self.assertEqual(ccw(topology.EAST),       topology.NORTH_EAST)
		self.assertEqual(ccw(topology.NORTH_EAST), topology.NORTH)
		self.assertEqual(ccw(topology.NORTH),      topology.WEST)
		self.assertEqual(ccw(topology.WEST),       topology.SOUTH_WEST)
		self.assertEqual(ccw(topology.SOUTH_WEST), topology.SOUTH)
		self.assertEqual(ccw(topology.SOUTH),      topology.EAST)
	
	def test_opposite(self):
		opp = topology.opposite
		
		self.assertEqual(opp(topology.EAST),       topology.WEST)
		self.assertEqual(opp(topology.NORTH_EAST), topology.SOUTH_WEST)
		self.assertEqual(opp(topology.NORTH),      topology.SOUTH)
		self.assertEqual(opp(topology.WEST),       topology.EAST)
		self.assertEqual(opp(topology.SOUTH_WEST), topology.NORTH_EAST)
		self.assertEqual(opp(topology.SOUTH),      topology.NORTH)
	
	def test_direction(self):
		ad = topology.add_direction
		
		self.assertEqual(ad((11,11,11), topology.EAST),       (12,11,11))
		self.assertEqual(ad((11,11,11), topology.NORTH_EAST), (11,11,10))
		self.assertEqual(ad((11,11,11), topology.NORTH),      (11,12,11))
		self.assertEqual(ad((11,11,11), topology.WEST),       (10,11,11))
		self.assertEqual(ad((11,11,11), topology.SOUTH_WEST), (11,11,12))
		self.assertEqual(ad((11,11,11), topology.SOUTH),      (11,10,11))
	
	
	def test_manhattan(self):
		self.assertEqual(topology.manhattan([0]),      0)
		self.assertEqual(topology.manhattan([1]),      1)
		self.assertEqual(topology.manhattan([-1]),     1)
		self.assertEqual(topology.manhattan([-1, 0]),  1)
		self.assertEqual(topology.manhattan([-1, -1]), 2)
		self.assertEqual(topology.manhattan([-1,  1]), 2)
	
	
	def test_median_element(self):
		self.assertEqual(topology.median_element([0]), 0)
		self.assertEqual(topology.median_element([0,1,2]), 1)
		self.assertEqual(topology.median_element([2,1,0]), 1)
		self.assertEqual(topology.median_element([1,2,0]), 1)
		self.assertEqual(topology.median_element([2,0,1]), 1)
		self.assertEqual(topology.median_element([2,2,2]), 2)
	
	
	def test_to_shortest_path(self):
		self.assertEqual(topology.to_shortest_path((0,0,0)), (0,0,0))
		self.assertEqual(topology.to_shortest_path((1,1,1)), (0,0,0))
		self.assertEqual(topology.to_shortest_path((0,1,2)), (-1,0,1))
		self.assertEqual(topology.to_shortest_path((-2,0,2)), (-2,0,2))
	
	
	def test_to_xy(self):
		self.assertEqual(topology.to_xy((0,0,0)), (0,0))
		self.assertEqual(topology.to_xy((1,1,1)), (0,0))
		self.assertEqual(topology.to_xy((0,1,2)), (-2,-1))
		self.assertEqual(topology.to_xy((-2,0,2)), (-4,-2))
	
	
	def test_to_xyz(self):
		self.assertEqual(topology.to_shortest_path(topology.to_xyz((0,0))), (0,0,0))
		self.assertEqual(topology.to_shortest_path(topology.to_xyz((0,1))), (0,1,0))
		self.assertEqual(topology.to_shortest_path(topology.to_xyz((1,0))), (1,0,0))
		self.assertEqual(topology.to_shortest_path(topology.to_xyz((1,1))), (0,0,-1))
	
	
	def test_to_torus_shortest_path(self):
		# Test exhaustively for various system sizes. Check that the results match
		# the theoretical length described by Xiao in "Hexagonal and Pruned Torus
		# Networks as Cayley Graphs" (2004)
		for system_size in [ (1,1) , (2,2) , (3,3), (4,4)
		                   , (1,2) , (2,1)
		                   , (1,3) , (3,1)
		                   ]:
			for y1 in range(system_size[1]):
				for x1 in range(system_size[0]):
					for y2 in range(system_size[1]):
						for x2 in range(system_size[0]):
							l = system_size[0]
							k = system_size[1]
							a = ((x2-x1) + l) % l
							b = ((y2-y1) + k) % k
							dist = min(min(min(max(a, b), max(l - a, k - b)), l - a + b), k + a - b);
							
							self.assertEqual( dist
							                , topology.manhattan(
							                    topology.to_torus_shortest_path( (x1, y1)
							                                                   , (x2, y2)
							                                                   , system_size
							                                                   )
							                  )
							                )
	
	
	def test_hexagon(self):
		it = topology.hexagon(2)
		
		# Inner layer
		self.assertEqual(it.next(), ( 0, 0))
		self.assertEqual(it.next(), (-1, 0))
		self.assertEqual(it.next(), ( 0, 1))
		
		# Outer layer
		self.assertEqual(it.next(), ( 1, 1))
		self.assertEqual(it.next(), ( 1, 0))
		self.assertEqual(it.next(), ( 0,-1))
		self.assertEqual(it.next(), (-1,-1))
		self.assertEqual(it.next(), (-2,-1))
		self.assertEqual(it.next(), (-2, 0))
		self.assertEqual(it.next(), (-1, 1))
		self.assertEqual(it.next(), ( 0, 2))
		self.assertEqual(it.next(), ( 1, 2))
		
		# Stop now
		self.assertRaises(StopIteration, it.next)
	
	
	def test_threeboards(self):
		# Creating no threeboards makes no boards...
		self.assertEqual(list(topology.threeboards(0)), [])
		
		# Creating 2x2 threeboards (throw away the boards...)
		boards = [topology.to_xy(c) for c in topology.threeboards(2)]
		self.assertEqual(len(boards), 3*2*2)
		# Threeboard (0,0)
		self.assertTrue((0,0) in boards)
		self.assertTrue((0,1) in boards)
		self.assertTrue((1,1) in boards)
		# Threeboard (1,0)
		self.assertTrue((2,1) in boards)
		self.assertTrue((2,2) in boards)
		self.assertTrue((3,2) in boards)
		# Threeboard (0,1)
		self.assertTrue((-1,1) in boards)
		self.assertTrue((-1,2) in boards)
		self.assertTrue((0,2) in boards)
		# Threeboard (1,1)
		self.assertTrue((1,2) in boards)
		self.assertTrue((1,3) in boards)
		self.assertTrue((2,3) in boards)



class ModelTests(unittest.TestCase):
	"""
	Tests the functions of living within the model.
	"""
	
	def test_node(self):
		n1 = model.Node([12,13])
		n2 = model.Node([21,23])
		n3 = model.Node([31,32])
		
		# Connect three nodes together in a chain
		n1.connect(12, n2, 21)
		n2.connect(23, n3, 32)
		
		# Check both connections exist and work both ways
		self.assertEqual(n1.connections[12], n2)
		self.assertEqual(n2.connections[21], n1)
		self.assertEqual(n2.connections[23], n3)
		self.assertEqual(n3.connections[32], n2)
		
		# Disconnect the connections and check this occurred
		n2.disconnect(21)
		n3.disconnect(32)
		self.assertIsNone(n1.connections[12])
		self.assertIsNone(n1.connections[13])
		self.assertIsNone(n2.connections[21])
		self.assertIsNone(n2.connections[23])
		self.assertIsNone(n3.connections[31])
		self.assertIsNone(n3.connections[32])


class UtilTests(unittest.TestCase):
	"""
	Tests that the various utility functions generate valid networks as
	they claim.
	"""
	
	def test_make_chip(self):
		"""
		Test that when a chip is created the correct number of cores are made and
		they are connected to the correct ports of the associated router.
		"""
		for num_cores in range(1,18+1):
			router, cores = model.make_chip(num_cores = num_cores)
			# The correct number of cores is created
			self.assertEqual(len(cores), num_cores)
			
			# The cores are connected correctly
			for core in cores.itervalues():
				# Core connects to router
				self.assertEqual( core.connections[model.Core.NETWORK_PORT]
				                , router
				                )
				# Router connects to core
				self.assertEqual( router.connections[model.Router.INTERNAL_PORTS[core.core_id]]
				                , core
				                )
			
			# No external ports are connected
			for port in model.Router.EXTERNAL_PORTS:
				self.assertIsNone(router.connections[port])
	
	
	def test_core_to_router(self):
		"""
		Test that the core-to-router function does what it says on the tin.
		"""
		router, cores = model.make_chip()
		for core in cores.itervalues():
			self.assertEqual(model.core_to_router(core), router)
	
	
	def test_is_path_connected(self):
		"""
		Test that the is_path_connected function works on a set of example cases.
		"""
		
		chips = model.make_rectangular_board(4,1)
		
		for is_connected, path in [ # Self-loop
		                            (True, [chips[(0,0)].cores[0], chips[(0,0)].router, chips[(0,0)].cores[0]]),
		                            # From one end to another
		                            (True, [ chips[(0,0)].cores[10], chips[(0,0)].router, chips[(1,0)].router
		                                   , chips[(2,0)].router, chips[(3,0)].router, chips[(3,0)].cores[11]
		                                   ]),
		                            # Reverse direction...
		                            (True, [ chips[(3,0)].cores[10], chips[(3,0)].router, chips[(2,0)].router
		                                   , chips[(1,0)].router, chips[(0,0)].router, chips[(0,0)].cores[11]
		                                   ]),
		                            # Self loop without router
		                            (False, [chips[(0,0)].cores[0], chips[(0,0)].cores[0]]),
		                            # From one chip to another non-adjacent chip
		                            (False, [ chips[(0,0)].cores[10], chips[(0,0)].router
		                                    , chips[(2,0)].router, chips[(2,0)].cores[11]
		                                    ]),
		                          ]:
			self.assertEqual(is_connected, model.is_path_connected(path))
	
	
	def test_fully_connect_chips_singleton_no_wrap_around(self):
		"""
		Test that model.fully_connect_chips doesn't add any connections to a
		singleton chip.
		"""
		chips = {(0,0):model.make_chip()}
		model.fully_connect_chips(chips)
		
		# No external ports are connected
		for port in model.Router.EXTERNAL_PORTS:
			self.assertIsNone(chips[(0,0)].router.connections[port])
	
	
	def test_fully_connect_chips_singleton_wrap_around(self):
		"""
		Test that model.fully_connect_chips adds wrap-around connections for all
		edges of a single chip.
		"""
		chips = {(0,0):model.make_chip()}
		model.fully_connect_chips(chips, wrap_around = True)
		
		# All connections are wrapped around
		for port in model.Router.EXTERNAL_PORTS:
			self.assertEqual( chips[(0,0)].router.connections[port]
			                , chips[(0,0)].router
			                )
	
	
	def test_fully_connect_chips_pair_of_chips_no_wrap_around(self):
		"""
		Test that a model.fully_connect_chips connects (and leaves disconnected)
		the correct links when a pair of touching chips are created.
		"""
		# Test with the neighbouring chip being on every possible edge.
		for direction in [ topology.EAST
		                 , topology.NORTH_EAST
		                 , topology.NORTH
		                 , topology.WEST
		                 , topology.SOUTH_WEST
		                 , topology.SOUTH
		                 ]:
			other_chip_position = topology.to_xy(topology.add_direction((0,0,0), direction))
			chips = { (0,0)               : model.make_chip((0,0))
			        , other_chip_position : model.make_chip(other_chip_position)
			        }
			model.fully_connect_chips(chips)
			
			# Only the touching ports are connected
			for port in model.Router.EXTERNAL_PORTS:
				if port == direction:
					# Touching port
					self.assertEqual( chips[(0,0)].router.connections[port]
					                , chips[other_chip_position].router
					                )
					self.assertEqual( chips[other_chip_position].router.connections[topology.opposite(port)]
					                , chips[(0,0)].router
					                )
				else:
					# Non-touching port
					self.assertIsNone(chips[(0,0)].router.connections[port])
					self.assertIsNone(chips[other_chip_position].router.connections[topology.opposite(port)])
	
	
	def test_make_rectangular_board(self):
		"""
		Test that a model.make_rectangular_board creates the appropriate formation
		of chips.
		"""
		for (w,h) in [(1,1), (1,2), (2,1), (2,2)]:
			chips = model.make_rectangular_board(w,h)
			
			# Ensure correct number of nodes
			self.assertEqual(len(chips), w*h)
			
			# Ensure nodes exist in correct places
			for y in range(h):
				for x in range(w):
					self.assertIn((x,y), chips.keys())
	
	
	def test_make_hexagonal_board(self):
		"""
		Test that model.make_hexagonal_board creates the appropriate formation of
		chips.
		"""
		for layers in [2,3,4]:
			chips = model.make_hexagonal_board(layers)
			ref_positions = list(topology.hexagon(layers))
			
			# Ensure correct number of nodes
			self.assertEqual(len(chips), len(ref_positions))
			
			# Ensure nodes exist in correct places
			for ref_position in ref_positions:
				self.assertIn(ref_position, chips.keys())
	
	
	def test_make_multiboard_torus(self):
		"""
		Test that model.make_multi_board_torus creates the appropriate (i.e.
		continuous, rectangular) formation of chips.
		"""
		for (w,h) in [(1,1), (1,2), (2,1), (2,2)]:
			chips = model.make_multi_board_torus(w,h)
			
			# Ensure correct number of nodes
			self.assertEqual(len(chips), w*12*h*12)
			
			# Ensure nodes exist in correct places
			for y in range(h*12):
				for x in range(w*12):
					self.assertIn((x,y), chips.keys())
	
	
	def test_get_all_routes_empty(self):
		"""
		Test that model.get_all_routes finds none in a system without any...
		"""
		chips = model.make_rectangular_board()
		self.assertEqual(model.get_all_routes(chips), {})
	
	
	def test_get_all_routes_empty(self):
		"""
		Test that model.get_all_routes finds some in a system containing some
		"""
		chips = model.make_rectangular_board(2,2)
		
		# A set of test routes
		ref_routes = {
			# Unicast self loop
			model.Route(0): (chips[(0,0)].cores[0], set([chips[(0,0)].cores[0]])),
			
			# Broadcast to all cores on a chip
			model.Route(1): (chips[(0,0)].cores[0], set(chips[(0,0)].cores.itervalues())),
			
			# Multicast messages from everyone from them to two other chips
			model.Route(2): (chips[(0,0)].cores[0], set([chips[(1,0)].cores[0], chips[(1,1)].cores[1]])),
			model.Route(3): (chips[(1,0)].cores[0], set([chips[(0,0)].cores[0], chips[(0,1)].cores[1]])),
			model.Route(4): (chips[(0,1)].cores[0], set([chips[(1,1)].cores[0], chips[(1,0)].cores[1]])),
			model.Route(5): (chips[(1,1)].cores[0], set([chips[(0,1)].cores[0], chips[(0,0)].cores[1]])),
		}
		
		# Add the reference routes to the network
		for route, (source, sinks) in ref_routes.iteritems():
			source.sources.add(route)
			for sink in sinks:
				sink.sinks.add(route)
		
		# Check that the routes found match the routes added
		found_routes = model.get_all_routes(chips)
		self.assertEqual(len(found_routes), len(ref_routes))
		for route, (source, sinks) in found_routes.iteritems():
			self.assertEqual(ref_routes[route][0], source)
			self.assertEqual(ref_routes[route][1], sinks)
	
	
	def test_add_route(self):
		"""
		Test that model.add_route successfully works for a simple multicast route (and
		that defining the route twice has no ill-effects).
		"""
		chips = model.make_rectangular_board(2,2)
		
		# Make a path travelling round the system (do it twice to make sure nothing
		# gets duplicated)
		route = model.Route(0)
		for _ in range(2):
			model.add_route( route
			               , [ chips[(0,0)].cores[0]
			                 , chips[(0,0)].router
			                 , chips[(0,1)].router
			                 , chips[(1,1)].router
			                 , chips[(1,0)].router
			                 , chips[(1,0)].cores[17]
			                 ]
			               )
			model.add_route( route
			               , [ chips[(0,0)].cores[0]
			                 , chips[(0,0)].router
			                 , chips[(0,1)].router
			                 , chips[(1,1)].router
			                 , chips[(1,1)].cores[17]
			                 ]
			               )
		
		# Check that the route was added in the appropriate sink/source and nowhere
		# else
		for (position, core) in sum(( list((router.position, core) for core in cores.itervalues())
		                              for (router,cores) in chips.itervalues()
		                            ), []):
			# Source should be in chip (0,0)'s 0th core
			if position == (0,0) and core.core_id == 0:
				self.assertEqual(core.sources, set([route]))
			else:
				self.assertEqual(core.sources, set())
			
			# Sink should be in chips (1,0)'s and (1,1)'s 17th core
			if position in ((1,0), (1,1)) and core.core_id == 17:
				self.assertEqual(core.sinks, set([route]))
			else:
				self.assertEqual(core.sinks, set())
		
		
		# Check that all connecting edges between routers are valid (i.e. face in
		# opposite directions and make sense)
		for router, cores in chips.itervalues():
			for route, (input_port, output_ports) in router.routes.iteritems():
				# Test the input has a corresponding output in the router/core
				if input_port in model.Router.INTERNAL_PORTS:
					# If a route is from a core, make sure the core knows about it
					core = router.connections[input_port]
					self.assertIn(route, core.sources)
				else:
					# Check the corresponding router has an output for this route pointing
					# at this router.
					other_router = router.connections[input_port]
					self.assertIn( topology.opposite(input_port)
					             , other_router.routes[route][1]
					             )
				
				# Test all outputs have a coresponding input in another router/core
				for output_port in output_ports:
					if output_port in model.Router.INTERNAL_PORTS:
						# If a route is to a core, make sure the core knows about it
						core = router.connections[output_port]
						self.assertIn(route, core.sinks)
					else:
						# Check the corresponding router has an input for this route pointing
						# from this router.
						other_router = router.connections[output_port]
						self.assertEqual( topology.opposite(output_port)
						                , other_router.routes[route][0]
						                )



class RoutersTests(unittest.TestCase):
	"""
	Tests the routing algorithms.
	"""
	
	def test_dor_perfect_case(self):
		"""
		Test dimension-order-routing in the case where routing should be possible.
		"""
		
		width  = 5
		height = 5
		
		port_to_dimension = {
			topology.EAST: 0,
			topology.WEST: 0,
			topology.NORTH: 1,
			topology.SOUTH: 1,
			topology.NORTH_EAST: 2,
			topology.SOUTH_WEST: 2,
		}
		
		for wrap_around in (True, False):
			chips = model.make_rectangular_board(width, height, wrap_around = wrap_around)
			for dimension_order in ( (0,1,2), (2,1,0) ):
				for route, source, sinks in ( # Self-loop
				                              (model.Route(0), chips[(0,0)].cores[0], ( chips[(0,0)].cores[0], )),
				                              # One-to-one (same row)
				                              (model.Route(1), chips[(0,0)].cores[0], ( chips[(4,0)].cores[0], )),
				                              # One-to-one (different row)
				                              (model.Route(2), chips[(0,0)].cores[0], ( chips[(2,1)].cores[0], )),
				                              # One-to-one (may use wrap-around)
				                              (model.Route(3), chips[(0,0)].cores[0], ( chips[(4,4)].cores[0], )),
				                              # One-to-N
				                              (model.Route(4), chips[(0,0)].cores[0], ( chips[(0,0)].cores[0]
				                                                                   , chips[(4,0)].cores[0]
				                                                                   , chips[(0,4)].cores[0]
				                                                                   , chips[(4,4)].cores[0]
				                                                                   )),
				                            ):
					node_sequences, unrouted_sinks = \
						routers.dimension_order_route(source, sinks, chips
						                             , use_wrap_around = wrap_around
						                             , dimension_order = dimension_order
						                             )
					
					# Nothing should be unroutable
					self.assertFalse(unrouted_sinks)
					
					# Should be one route per sink
					self.assertEqual(len(sinks), len(node_sequences))
					
					# All node sequences should start from the source
					for node_sequence in node_sequences:
						self.assertEqual(node_sequence[0], source)
					
					sinks_routed = set()
					for node_sequence in node_sequences:
						sequence_sink = node_sequence[-1]
						# Each sink must not have multiple node sequences leading to it
						self.assertNotIn(sequence_sink, sinks_routed)
						sinks_routed.add(sequence_sink)
					
					# Every sink must have node sequence leading to it
					self.assertEqual(set(sinks), sinks_routed)
					
					# Test that the route follows the order of dimensions required
					for node_sequence in node_sequences:
						dimensions = list(dimension_order)
						for step in xrange(1, len(node_sequence) - 2):
							router = node_sequence[step]
							next_router = node_sequence[step+1]
							
							# Find the port to the next router
							for port, next_router_ in router.connections.iteritems():
								if next_router_ == next_router:
									break
								port = None
							
							# Whenever the direction changes, it must change to a direction
							# next in the ordering
							while dimensions[0] != port_to_dimension[port]:
								dimensions.pop(0)
								self.assertTrue(dimensions)
	
	
	def test_dor_dead_links(self):
		"""
		Test dimension-order-routing in the case where routing is not possible.
		"""
		# Create a square system with a hole in the x-axis for the 0th row of chips.
		chips = model.make_rectangular_board(3, 1)
		chips[(1,0)].router.connections[topology.EAST] = None
		
		# Should not be able to route along the x axis of the system.
		node_sequences, unrouted_sinks = \
			routers.dimension_order_route( chips[(0,0)].cores[0]
			                             , [chips[(2,0)].cores[0]]
			                             , chips
			                             , use_wrap_around = False
			                             , dimension_order = (0,1,2)
			                             )
		
		self.assertFalse(node_sequences)
		self.assertEqual(len(unrouted_sinks), 1)



class TableGenTests(unittest.TestCase):
	"""
	Tests the routing table generation facilities.
	"""
	
	def setUp(self):
		"""
		Create a small network with a few routes within it.
		"""
		
		self.chips = model.make_rectangular_board(3,3)
		
		# A self-loop on 0,1,0
		model.add_route(model.Route(0), [ self.chips[(0,1)].cores[0]
		                                , self.chips[(0,1)].router
		                                , self.chips[(0,1)].cores[0]
		                                ])
		
		# A straight route from 0,0,0 to 2,0,0
		model.add_route(model.Route(1), [ self.chips[(0,0)].cores[0]
		                                , self.chips[(0,0)].router
		                                , self.chips[(1,0)].router
		                                , self.chips[(2,0)].router
		                                , self.chips[(2,0)].cores[0]
		                                ])
		
		# A multicast from from 0,2,0 to 1,2,0,  2,2,0 and 1,1,0
		r = model.Route(2)
		model.add_route(r, [ self.chips[(0,2)].cores[0]
		                   , self.chips[(0,2)].router
		                   , self.chips[(1,2)].router
		                   , self.chips[(1,2)].cores[0]
		                   ])
		model.add_route(r, [ self.chips[(0,2)].cores[0]
		                   , self.chips[(0,2)].router
		                   , self.chips[(1,2)].router
		                   , self.chips[(2,2)].router
		                   , self.chips[(2,2)].cores[0]
		                   ])
		model.add_route(r, [ self.chips[(0,2)].cores[0]
		                   , self.chips[(0,2)].router
		                   , self.chips[(1,2)].router
		                   , self.chips[(1,1)].router
		                   , self.chips[(1,1)].cores[0]
		                   ])
		
		# A self-loop on 1,1,1 to result in 1,1 having multiple routing entries
		model.add_route(model.Route(3), [ self.chips[(1,1)].cores[1]
		                                , self.chips[(1,1)].router
		                                , self.chips[(1,1)].cores[1]
		                                ])
	
	
	def test_empty_router(self):
		"""
		Ensure an empty table is produced given an empty router.
		"""
		# Just the terminating 1s
		self.assertEqual( table_gen.ybug_table_gen(self.chips[(2,1)].router)
		                , "\xFF"*16
		                )
	
	
	def test_automatic_route(self):
		"""
		Ensure that routers only required to perform automatic routing are
		ignored...
		"""
		# Just the terminating 1s
		self.assertEqual( table_gen.ybug_table_gen(self.chips[(1,0)].router)
		                , "\xFF"*16
		                )
	
	
	def test_self_loop(self):
		"""
		Ensure that routes sourced from a core and destined for another core come
		out correctly.
		"""
		# Just the self-loop
		self.assertEqual( table_gen.ybug_table_gen(self.chips[(0,1)].router)
		                  # Index      # Num rows   # Route              # Key                # Mask
		                , "\x00\x00" + "\x01\x00" + "\x40\x00\x00\x00" + "\x00\x00\x00\x00" + "\xFF\xFF\xFF\xFF"
		                  + "\xFF"*16
		                )
	
	
	def test_enter_network(self):
		"""
		Ensure that routes sourced from a core and destined for another chip is
		routed appropriately.
		"""
		# Just the entry route
		self.assertEqual( table_gen.ybug_table_gen(self.chips[(0,0)].router)
		                  # Index      # Num rows   # Route              # Key                # Mask
		                , "\x00\x00" + "\x01\x00" + "\x01\x00\x00\x00" + "\x01\x00\x00\x00" + "\xFF\xFF\xFF\xFF"
		                  + "\xFF"*16
		                )
	
	
	def test_leave_network(self):
		"""
		Ensure that routes sourced from another router and destined for a core
		routed appropriately.
		"""
		# Just the exit route
		self.assertEqual( table_gen.ybug_table_gen(self.chips[(2,0)].router)
		                  # Index      # Num rows   # Route              # Key                # Mask
		                , "\x00\x00" + "\x01\x00" + "\x40\x00\x00\x00" + "\x01\x00\x00\x00" + "\xFF\xFF\xFF\xFF"
		                  + "\xFF"*16
		                )
	
	
	def test_fork(self):
		"""
		Ensure that routes fork successfully.
		"""
		# Should route to all three locations required.
		self.assertEqual( table_gen.ybug_table_gen(self.chips[(1,2)].router)
		                  # Index      # Num rows   # Route              # Key                # Mask
		                , "\x00\x00" + "\x01\x00" + "\x61\x00\x00\x00" + "\x02\x00\x00\x00" + "\xFF\xFF\xFF\xFF"
		                  + "\xFF"*16
		                )
	
	
	def test_multiple(self):
		"""
		Ensure that a router with multiple entries can exist
		"""
		table = table_gen.ybug_table_gen(self.chips[(1,1)].router)
		
		# Should have two router entries (plus a terminator)
		self.assertEqual(len(table), 16*3)
		self.assertEqual(table[-16:], "\xFF"*16)
		
		EXPECTED_ENTRIES = {
			"\x02\x00\x00\x00": "\x40\x00\x00\x00",
			"\x03\x00\x00\x00": "\x80\x00\x00\x00",
		}
		
		for entry_num in range(2):
			# Each routing entry should be numbered consecutively
			self.assertEqual( table[entry_num*16:entry_num*16+4]
			                , chr(entry_num) + "\x00\x02\x00"
			                )
			
			# Check the router entry is as expected for the key (and only once)
			self.assertEqual( EXPECTED_ENTRIES.pop(table[entry_num*16+8:entry_num*16+12], None)
			                , table[entry_num*16+4:entry_num*16+8]
			                )
			
			# Each entry should have an all-ones mask
			self.assertEqual( table[entry_num*16+12:entry_num*16+16]
			                , "\xFF\xFF\xFF\xFF"
			                )
		
		# No expected entries were missing
		self.assertEqual(len(EXPECTED_ENTRIES), 0)



if __name__=="__main__":
	unittest.main()
