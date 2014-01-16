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
