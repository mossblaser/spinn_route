#!/usr/bin/env python

"""
Utilities for working with coordinates of various types, notably ones in
hexagonal space.

Uses the hexagonal addressing scheme suggested in

	Addressing and Routing in Hexagonal Networks with Applications for Tracking
	Mobile Users and Connection Rerouting in Cellular Networks by Nocetti et. al.
"""

################################################################################
# Directions
################################################################################

EAST       = 0
NORTH_EAST = 1
NORTH      = 2
WEST       = 3
SOUTH_WEST = 4
SOUTH      = 5


def next_ccw(direction):
	"""
	Returns the next direction counter-clockwise from the given direction.
	"""
	return (direction+1)%6


def next_cw(direction):
	"""
	Returns the next direction counter-clockwise from the given direction.
	"""
	return (direction-1)%6


def opposite(direction):
	"""
	Returns the opposite direction
	"""
	return (direction+3)%6


################################################################################
# Coordinates in hexagon world :)
################################################################################

def add_direction(vector, direction):
	"""
	Returns the vector moved one unit in the given direction.
	"""
	add = {
		EAST:       ( 1, 0, 0),
		WEST:       (-1, 0, 0),
		NORTH:      ( 0, 1, 0),
		SOUTH:      ( 0,-1, 0),
		NORTH_EAST: ( 0, 0,-1),
		SOUTH_WEST: ( 0, 0, 1),
	}
	
	return tuple((v + a for (v,a) in zip(vector, add[direction])))


def manhattan(vector):
	"""
	Calculate the Manhattan distance required to traverse the given vector.
	"""
	return sum(map(abs, vector))


def median_element(values):
	"""
	Returns the value of the median element of the set.
	"""
	return sorted(values)[len(values)/2]


def to_shortest_path(vector):
	"""
	Converts a vector into the shortest-path variation.
	
	A shortest path has at least one dimension equal to zero and the remaining two
	dimensions have opposite signs (or are zero).
	"""
	assert(len(vector) == 3)
	
	# The vector (1,1,1) has distance zero so this can be added or subtracted
	# freely without effect on the destination reached. As a result, simply
	# subtract the median value from all dimensions to yield the shortest path.
	median = median_element(vector)
	return tuple((v - median for v in vector))


def to_xy(vector):
	"""
	Takes a 3D vector and returns the equivalent 2D version.
	"""
	return (vector[0] - vector[2], vector[1] - vector[2])


def to_xyz(vector):
	"""
	Takes a 2D vector and returns the equivalent (non-minimal) 3D version.
	"""
	return (vector[0], vector[1], 0)


def to_torus_shortest_path(src, dst, bounds = None):
	"""
	Gets the shortest path from src to dst.
	
	If bounds is given it must be a 2-tuple specifying the (x,y) dimensions of the
	mesh size. The path will then be allowed to 'wrap-around', otherwise it will
	not.
	
	This algorithm is based on the one used by INSEE.
	"""
	assert(len(src) == len(dst) == 2)
	assert(bounds is None or len(bounds) == 2)

	# Special case for self-loop
	if src == dst:
		return (0,0,0)

	# The distances between s and t for non-wrapping and always wrapping routes
	# for x and y axes respectively.
	dx_nw = dst[0] - src[0]
	dy_nw = dst[1] - src[1]
	dx_aw = (dx_nw - bounds[0]) if (dx_nw > 0) else (dx_nw + bounds[0])
	dy_aw = (dy_nw - bounds[1]) if (dy_nw > 0) else (dy_nw + bounds[1])

	best_vect = None
	def try_vect(vect):
		if best_vect is None or manhattan(vect) < manhattan(best_vect):
			return vect
		else:
			return best_vect

	# Try the non-wrapping possibilities using only x,z, y,z and x,y
	best_vect = try_vect((dx_nw - dy_nw, 0, -dy_nw))
	best_vect = try_vect((0, dy_nw - dx_nw, -dx_nw))
	best_vect = try_vect((dx_nw, dy_nw, 0))

	# Try the x-non-wrapping, y-wrapping possibilities using only x,z, y,z and x,y
	best_vect = try_vect((dx_nw - dy_aw, 0, -dy_aw))
	best_vect = try_vect((0, dy_aw - dx_nw, -dx_nw))
	best_vect = try_vect((dx_nw, dy_aw, 0))

	# Try the x-wrapping, y-non-wrapping possibilities using only x,z, y,z and x,y
	best_vect = try_vect((dx_aw - dy_nw, 0, -dy_nw))
	best_vect = try_vect((0, dy_nw - dx_aw, -dx_aw))
	best_vect = try_vect((dx_aw, dy_nw, 0))

	# Try the x-wrapping, y-wrapping possibilities using only x,z, y,z and x,y
	best_vect = try_vect((dx_aw - dy_aw, 0, -dy_aw))
	best_vect = try_vect((0, dy_aw - dx_aw, -dx_aw))
	best_vect = try_vect((dx_aw, dy_aw, 0))

	return best_vect;


################################################################################
# Hexagon Generation
################################################################################

def hexagon(layers = 4):
	"""
	Generator which produces a list of (x,y) tuples which produce a hexagon of the
	given number of layers.
	
	Try me::
	
		points = set(hexagon(4))
		for y in range(min(y for (x,y) in points), max(y for (x,y) in points) + 1)[::-1]:
			for x in range(min(x for (x,y) in points), max(x for (x,y) in points) + 1):
				if (x,y) in points:
					print "#",
				else:
					print " ",
			print
	"""
	
	X,Y,Z = 0,1,2
	
	next_position = [0,0,0]
	
	for n in range(layers):
		for _ in range(n):
			yield to_xy(next_position)
			next_position[Y] -= 1
		
		for _ in range(n):
			yield to_xy(next_position)
			next_position[Z] += 1
		
		for _ in range(n+1):
			yield to_xy(next_position)
			next_position[X] -= 1
		
		for _ in range(n):
			yield to_xy(next_position)
			next_position[Y] += 1
		
		for _ in range(n+1):
			yield to_xy(next_position)
			next_position[Z] -= 1
		
		for _ in range(n+1):
			yield to_xy(next_position)
			next_position[X] += 1




################################################################################
# Threeboard Generation
################################################################################


def threeboards(width = 1, height = None):
	r"""
	Generates a list of width x height threeboards. If height is not specified,
	height = width. Width defaults to 1. Coordinates are given as (x,y,0) tuples
	on a hexagonal coordinate system like so::
		
		
		    | y
		    |
		   / \
		z /   \ x
	
	A threeboard looks like so::
		
		   ___
		  / 1 \___
		  \___/ 2 \
		  / 0 \___/
		  \___/
	
	With the bottom-left hexagon being at (0,0).
	
	And is tiled in to long rows like so::
		
		   ___     ___     ___     ___
		  / 0 \___/ 1 \___/ 2 \___/ 3 \___
		  \___/ 0 \___/ 1 \___/ 2 \___/ 3 \
		  / 0 \___/ 1 \___/ 2 \___/ 3 \___/
		  \___/   \___/   \___/   \___/
	
	And into a mesh like so::
		
		   ___     ___     ___     ___
		  / 4 \___/ 5 \___/ 6 \___/ 7 \___
		  \___/ 4 \___/ 5 \___/ 6 \___/ 7 \
		  / 4 \___/ 5 \___/ 6 \___/ 7 \___/
		  \___/ 0 \___/ 1 \___/ 2 \___/ 3 \___
		      \___/ 0 \___/ 1 \___/ 2 \___/ 3 \
		      / 0 \___/ 1 \___/ 2 \___/ 3 \___/
		      \___/   \___/   \___/   \___/
	
	"""
	
	height = width if height is None else height
	
	# Create the boards
	for y in range(height):
		for x in range(width):
			# z is the index of the board within the set. 0 is the bottom left, 1 is
			# the top, 2 is the right
			for z in range(3):
				# Offset within threeboard --+
				# Y offset ---------+        |
				# X offset -+       |        |
				#           |       |        |
				x_coord = (x*2) + (-y) + (z >= 2)
				y_coord = (x  ) + ( y) + (z >= 1)
				yield (x_coord,y_coord,0)
