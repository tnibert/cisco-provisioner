from rip import passive_interface

ospf_setup = """
{version_init}
router-id {router_id}
{networks}
{passive_interfaces}
end
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

v2_init = """
router ospf {process_id}
"""

v3_init = """
ipv6 router ospf {process_id}
"""
