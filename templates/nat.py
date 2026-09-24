# static NAT
static_nat_setup = """
ip nat inside source static {local_ip} {global_ip}
"""

nat_inside = """
ip nat inside
"""

nat_outside = """
ip nat outside
"""

# dynamic NAT
dynamic_nat_pool_setup = """
ip nat pool {pool_name} {start_addr} {end_addr} netmask {netmask}
"""

bind_acl_pool = """
ip nat inside source list {acl_identifier} pool {pool_name}
"""

# PAT
pat_setup = """
ip nat inside source list {acl_identifier} interfaces {intf_type} {intf_number} overload
"""

bind_acl_pool_pat = bind_acl_pool + " overload\n"
