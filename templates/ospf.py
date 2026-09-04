from rip import passive_interface

ospf_setup = """
{version_init}
router-id {router_id}
{networks}
{passive_interfaces}
{summaries}
{asbr}
exit
"""

network = """
network {net_addr} {wildcard_mask} area {area_id}
"""

set_asbr = """
default-information originate
"""

route_summary_v2 = """
area {area} range {addr} {net_mask}
"""

route_summary_v3 = """
area {area} range {addr_mask}
"""

set_hello_ival = """
ip ospf hello-interval {seconds}
"""

set_dead_ival = """
ip ospf dead-interval {seconds}
"""

ipv6_point_to_point = """
ipv6 ospf network point-to-point
"""

"""
auto-cost reference-bandwidth {bandwidth}
"""

"""
ip ospf cost {}
"""

bandwidth_block = """
bandwidth {speed}
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
