from rip import passive_interface

ospf_setup = """
{version_init}
router-id {router_id}
{networks}
{passive_interfaces}
exit
"""

network = """
network {net_addr} {wildcard_mask} area {area_id}
"""

"""
auto-cost reference-bandwidth {bandwidth}
"""

"""
ip ospf cost {}
"""

"""
bandwidth {}
"""

v2_init = """
router ospf {process_id}
"""

v3_init = """
ipv6 router ospf {process_id}
"""

ipv6_interface = """
ipv6 ospf {process_id} area {area_id}
"""
