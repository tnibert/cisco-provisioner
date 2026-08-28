rip_setup = """
router rip
{networks}
version 2
{passive_interfaces}
{default_propagate}
no auto-summary
exit
"""

network = """
network {net_addr}
"""

passive_interface = """
passive-interface {intf}
"""

default_route_propagate = """
default-information originate
"""
