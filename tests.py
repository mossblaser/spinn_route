#!/usr/bin/env python

"""
Unit tests. Not comprehensive but just quick and dirty... Usage:

python tests.py
"""

import unittest

import topology
import model
import network

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


if __name__=="__main__":
	unittest.main()
