DHCP_V4_EXCLUDE = """
ip dhcp excluded-address {addr}
"""

DHCP_V4_POOL_CREATE = """
ip dhcp pool {pool_name}
network {net_addr} {mask}
default-router {gw}
{additional} 
"""

DHCP_V4_DNS = """
dns-server {addr}
"""

DHCP_V4_DOMAIN_NAME = """
domain-name {domain}
"""

DHCP_V4_RELAY = """
ip helper-address {addr}
"""
