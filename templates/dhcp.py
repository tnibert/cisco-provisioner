DHCP_V4_EXCLUDE = """
ip dhcp excluded-address {addr}
"""

DHCP_V4_POOL_CREATE = """
ip dhcp pool {pool_name}
network {net_addr} {mask}
default-router {gw}
{additional} 
"""

DHCP_DNS = """
dns-server {addr}
"""

DHCP_DOMAIN_NAME = """
domain-name {domain}
"""

DHCP_V4_RELAY = """
ip helper-address {addr}
"""

DHCP_V6_POOL_CREATE = """
ipv6 dhcp pool {pool_name}
{additional}
exit
"""

DHCP_V6_STATEFUL_POOL_PREFIX = """
address prefix {addr}
"""

# this is on a router port
DHCP_V6_SERVER_CREATE = """
ipv6 dhcp server {pool_name}
{flags}
"""

DHCP_V6_STATELESS_FLAGS = """
ipv6 nd other-config-flag
"""

DHCP_V6_STATEFUL_FLAGS = """
ipv6 nd managed-config-flag
ipv6 nd prefix default no-autoconfig
"""
