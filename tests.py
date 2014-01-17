#!/usr/bin/env python

"""
Unit tests. Not comprehensive but just quick and dirty... Usage:

python tests.py
"""

import unittest
import pprint

import topology
import model
import util

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
		n1 = model.Node([11,12])
		n2 = model.Node([21,22])
		
		# Connect two nodes together using different ports on either end
		n1.connect(11, n2, 21)
		n2.connect(22, n1, 12)
		
		# Check both connections exist and work both ways
		self.assertEqual(n1.connections[11], (n2, 21))
		self.assertEqual(n2.connections[21], (n1, 11))
		self.assertEqual(n1.connections[12], (n2, 22))
		self.assertEqual(n2.connections[22], (n1, 12))
		
		# Disconnect the connections and check this occurred
		n1.disconnect(12)
		n2.disconnect(21)
		self.assertIsNone(n1.connections[11])
		self.assertIsNone(n2.connections[21])
		self.assertIsNone(n1.connections[12])
		self.assertIsNone(n2.connections[22])


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
			router, cores = util.make_chip(num_cores = num_cores)
			# The correct number of cores is created
			self.assertEqual(len(cores), num_cores)
			
			# The cores are connected correctly
			for core in cores:
				# Core connects to router
				self.assertEqual( core.connections[model.Core.NETWORK_PORT]
				                , (router, model.Router.INTERNAL_PORTS[core.core_id])
				                )
				# Router connects to core
				self.assertEqual( router.connections[model.Router.INTERNAL_PORTS[core.core_id]]
				                , (core, model.Core.NETWORK_PORT)
				                )
			
			# No external ports are connected
			for port in model.Router.EXTERNAL_PORTS:
				self.assertIsNone(router.connections[port])
	
	
	def test_fully_connect_chips_singleton_no_wrap_around(self):
		"""
		Test that util.fully_connect_chips doesn't add any connections to a
		singleton chip.
		"""
		chips = [util.make_chip()]
		util.fully_connect_chips(chips)
		
		# No external ports are connected
		for port in model.Router.EXTERNAL_PORTS:
			self.assertIsNone(chips[0][0].connections[port])
	
	
	def test_fully_connect_chips_singleton_wrap_around(self):
		"""
		Test that util.fully_connect_chips adds wrap-around connections for all
		edges of a single chip.
		"""
		chips = [util.make_chip()]
		util.fully_connect_chips(chips, wrap_around = True)
		
		# All connections are wrapped around
		for port in model.Router.EXTERNAL_PORTS:
			self.assertEqual( chips[0][0].connections[port]
			                , (chips[0][0], topology.opposite(port))
			                )
	
	
	def test_fully_connect_chips_pair_of_chips_no_wrap_around(self):
		"""
		Test that a util.fully_connect_chips connects (and leaves disconnected)
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
			chips = [ util.make_chip((0,0))
			        , util.make_chip(topology.to_xy(topology.add_direction((0,0,0), direction)))
			        ]
			util.fully_connect_chips(chips)
			
			# Only the touching ports are connected
			for port in model.Router.EXTERNAL_PORTS:
				if port == direction:
					# Touching port
					self.assertEqual( chips[0][0].connections[port]
					                , (chips[1][0], topology.opposite(port))
					                )
					self.assertEqual( chips[1][0].connections[topology.opposite(port)]
					                , (chips[0][0], port)
					                )
				else:
					# Non-touching port
					self.assertIsNone(chips[0][0].connections[port])
					self.assertIsNone(chips[1][0].connections[topology.opposite(port)])
	
	
	def test_make_rectangular_board(self):
		"""
		Test that a util.make_rectangular_board creates the appropriate formation
		of chips.
		"""
		for (w,h) in [(1,1), (1,2), (2,1), (2,2)]:
			chips = util.make_rectangular_board(w,h)
			positions = [router.position for (router,cores) in chips]
			
			# Ensure correct number of nodes
			self.assertEqual(len(positions), w*h)
			
			# Ensure nodes exist in correct places
			for y in range(h):
				for x in range(w):
					self.assertIn((x,y), positions)
	
	
	def test_make_hexagonal_board(self):
		"""
		Test that util.make_hexagonal_board creates the appropriate formation of
		chips.
		"""
		for layers in [2,3,4]:
			chips = util.make_hexagonal_board(layers)
			ref_positions = list(topology.hexagon(layers))
			positions = [router.position for (router,cores) in chips]
			
			# Ensure correct number of nodes
			self.assertEqual(len(positions), len(ref_positions))
			
			# Ensure nodes exist in correct places
			for ref_position in ref_positions:
				self.assertIn(ref_position, positions)
	
	
	def test_make_multiboard_torus(self):
		"""
		Test that util.make_multi_board_torus creates the appropriate (i.e.
		continuous, rectangular) formation of chips.
		"""
		for (w,h) in [(1,1), (1,2), (2,1), (2,2)]:
			chips = util.make_multi_board_torus(w,h)
			positions = [router.position for (router,cores) in chips]
			
			# Ensure correct number of nodes
			self.assertEqual(len(positions), w*12*h*12)
			
			# Ensure nodes exist in correct places
			for y in range(h*12):
				for x in range(w*12):
					self.assertIn((x,y), positions)
	
	
	def test_get_all_routes_empty(self):
		"""
		Test that util.get_all_routes finds none in a system without any...
		"""
		chips = util.make_rectangular_board()
		self.assertEqual(util.get_all_routes(chips), {})
	
	
	def test_get_all_routes_empty(self):
		"""
		Test that util.get_all_routes finds some in a system containing some
		"""
		chips = util.make_rectangular_board(2,2)
		
		# A set of test routes
		ref_routes = {
			# Unicast self loop
			model.Route(0): (chips[0][1][0], set([chips[0][1][0]])),
			
			# Broadcast to all cores on a chip
			model.Route(1): (chips[0][1][0], set(chips[0][1])),
			
			# Multicast messages from everyone from them to the next two chips
			model.Route(2): (chips[0][1][0], set([chips[1][1][0], chips[1][1][1]])),
			model.Route(3): (chips[1][1][0], set([chips[2][1][0], chips[3][1][1]])),
			model.Route(4): (chips[2][1][0], set([chips[3][1][0], chips[0][1][1]])),
			model.Route(5): (chips[3][1][0], set([chips[0][1][0], chips[1][1][1]])),
		}
		
		# Add the reference routes to the network
		for route, (source, sinks) in ref_routes.iteritems():
			source.sources.add(route)
			for sink in sinks:
				sink.sinks.add(route)
		
		# Check that the routes found match the routes added
		found_routes = util.get_all_routes(chips)
		self.assertEqual(len(found_routes), len(ref_routes))
		for route, (source, sinks) in found_routes.iteritems():
			self.assertEqual(ref_routes[route][0], source)
			self.assertEqual(ref_routes[route][1], sinks)
	
	
	def test_add_route(self):
		"""
		Test that util.add_route successfully works for a simple multicast route (and
		that defining the route twice has no ill-effects).
		"""
		chips = util.make_rectangular_board(2,2)
		chip_map = {}
		for (router, core) in chips:
			chip_map[router.position] = (router, core)
		
		# Make a path travelling round the system (do it twice to make sure nothing
		# gets duplicated)
		route = model.Route(0)
		for _ in range(2):
			util.add_route( route
			              , [ chip_map[(0,0)][1][0]
			                , chip_map[(0,0)][0]
			                , chip_map[(0,1)][0]
			                , chip_map[(1,1)][0]
			                , chip_map[(1,0)][0]
			                , chip_map[(1,0)][1][17]
			                ]
			              )
			util.add_route( route
			              , [ chip_map[(0,0)][1][0]
			                , chip_map[(0,0)][0]
			                , chip_map[(0,1)][0]
			                , chip_map[(1,1)][0]
			                , chip_map[(1,1)][1][17]
			                ]
			              )
		
		# Check that the route was added in the appropriate sink/source and nowhere
		# else
		for (position, core) in sum(( list((router.position, core) for core in cores)
		                              for (router,cores) in chips
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
		for router, cores in chips:
			for route, (input_port, output_ports) in router.routes.iteritems():
				# Test the input has a corresponding output in the router/core
				if input_port in model.Router.INTERNAL_PORTS:
					# If a route is from a core, make sure the core knows about it
					core = router.connections[input_port][0]
					self.assertIn(route, core.sources)
				else:
					# Check the corresponding router has an output for this route pointing
					# at this router.
					other_router = router.connections[input_port][0]
					self.assertIn( router.connections[input_port][1]
					             , other_router.routes[route][1]
					             )
				
				# Test all outputs have a coresponding input in another router/core
				for output_port in output_ports:
					if output_port in model.Router.INTERNAL_PORTS:
						# If a route is to a core, make sure the core knows about it
						core = router.connections[output_port][0]
						self.assertIn(route, core.sinks)
					else:
						# Check the corresponding router has an input for this route pointing
						# from this router.
						other_router = router.connections[output_port][0]
						self.assertEqual( router.connections[output_port][1]
						                , other_router.routes[route][0]
						                )
		

if __name__=="__main__":
	unittest.main()
