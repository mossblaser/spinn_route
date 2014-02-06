#!/usr/bin/env python

"""
Example usage of the spinn_route module to generate routing tables for
SpiNNaker.

Creates multicast routes from every core and randomly selected destinations and
generates a routing table file for each router/chip.
"""

import random

from spinn_route import model, routers, table_gen


# The probability of generating a route from a given core to each other core in
# the system.
CONNECTION_PROB = 0.01/18


# Define a spinnaker system (in this example a 4-chip 2x2 Spinn-3 Board)
chips = model.make_rectangular_board(20,20)


# Get a list of all the cores in the system to randomly connect
all_cores = []
for position, (router, cores) in chips.iteritems():
	all_cores.extend(cores)

# Randomly create some routes between these cores
for routing_key, source_core in enumerate(all_cores):
	sink_cores  = [c for c in all_cores if random.random() <= CONNECTION_PROB]
	
	# Work the route to take using a simple dimension order routing scheme
	routes, unrouted_sinks = routers.dimension_order_route(source_core, sink_cores, chips)
	
	# Since our network doesn't have any faults, this should work perfectly
	assert(len(unrouted_sinks) == 0)
	
	# Add the routes to the routers
	route = model.Route(routing_key)
	for node_sequence in routes:
		model.add_route(route, node_sequence)


# Write out routing tables for all routers
for position, (router, cores) in chips.iteritems():
	table = table_gen.ybug_table_gen(router)
	
	with open("routing_table_%d_%d.bin"%position, "wb") as f:
		f.write(table)

