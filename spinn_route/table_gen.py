#!/usr/bin/env python

"""
Facilities for producing routing table files for ybug given a model.

Currently does not attempt to compress routing entries.
"""

import struct

import topology
import model

"""
The struct interpreted by SC&MP/ybug to describe a routing table entry.
"""
ybug_rtr_entry_t = struct.Struct( "<" # Little endian, standard sizes (i.e. 2-byte short, 4-byte int)
                                + "H" # ushort next (use when loading: index of the entry)
                                + "H" # ushort free (use when loading: total number of entries)
                                + "I" # uint   route
                                + "I" # uint   key
                                + "I" # uint   mask
                                )

"""
The struct interpreted by the spin1 API to describe a routing table entry.
"""
spin1_rtr_entry_t = struct.Struct( "<" # Little endian, standard sizes (i.e. 2-byte short, 4-byte int)
                                 + "I" # uint   key
                                 + "I" # uint   mask
                                 + "I" # uint   route
                                 )


"""
Encodings for router link directions.
"""
LINK_BITS = {
	topology.EAST       : 1<<0,
	topology.NORTH_EAST : 1<<1,
	topology.NORTH      : 1<<2,
	topology.WEST       : 1<<3,
	topology.SOUTH_WEST : 1<<4,
	topology.SOUTH      : 1<<5,
}
for core in range(18):
	LINK_BITS[model.Router.INTERNAL_PORTS[core]] = 1<<(core + 6)


def get_router_entries(router):
	"""
	Given a router, returns a list of (route_bits, key, mask) tuples.
	"""
	# A list of (route_bits, key, mask) tuples corresponding to the router entries
	# required.
	table_entries = []
	
	# Work out what routing entries are required
	for route, (incoming_port, outgoing_ports) in router.routes.iteritems():
		# Routes which simply forward packets without changing their
		# direction/forking are default routed and do not require a table entry.
		if not ( incoming_port in model.Router.EXTERNAL_PORTS \
		         and len(outgoing_ports) == 1 \
		         and topology.opposite(incoming_port) in outgoing_ports
		       ):
			route_bits = sum(LINK_BITS[port] for port in outgoing_ports)
			key = route.key
			mask = 0xFFFFFFFF
			table_entries.append((route_bits, key, mask))
	
	return table_entries


def ybug_table_gen(router):
	"""
	Generate a routing table description file for a given router based on the
	format used for loading by ybug.
	"""
	
	table_entries = get_router_entries(router)
	
	# Generate the binary formatted table entries
	out = ""
	for entry_num, (route_bits, key, mask) in enumerate(table_entries):
		out += ybug_rtr_entry_t.pack(entry_num, len(table_entries), route_bits, key, mask)
	
	# Terminate with an empty all-ones entry
	out += ybug_rtr_entry_t.pack(0xFFFF, 0xFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)
	
	return out


def spin1_table_gen(router):
	"""
	Generate a routing table description file suitable for loading via the
	spin1 API. Returns a tuple (num_entries, data) where data is a packed series of
	tripples key, mask and route.
	"""
	
	table_entries = get_router_entries(router)
	
	out = ""
	for entry_num, (route_bits, key, mask) in enumerate(table_entries):
		out += spin1_rtr_entry_t.pack(key, mask, route_bits)
	
	return len(table_entries), out
