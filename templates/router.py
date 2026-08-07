INTERFACE_BLOCK = """
interface {intf}
{body}
exit
"""

ENABLE_IPV6 = """
ipv6 unicast-routing
"""

CONFIG_IPV4_PORT = """
ip address {ipv4} {subnet_mask}
"""

CONFIG_IPV6_PORT = """
ipv6 address {ipv6}
"""

DCE = """
clock rate 128000
"""

CONFIG_LOOPBACK_IPV4 = """
interface loopback {number}
ip address {addr} {mask}
exit
"""

CONFIG_ROUTER_ON_A_STICK_BLOCK = """
int {port}.{vlan}
encapsulation dot1q {vlan}
ip address {gw} {mask}
{additional}
"""

CONFIG_NATIVE_ROUTER_ON_A_STICK_BLOCK = """
int {port}.{vlan}
encapsulation dot1q {vlan} native
"""

CONFIG_IPV6_BLOCK = """
int {port}.{vlan}
""" + CONFIG_IPV6_PORT

CONFIG_IPV6_LINK_LOCAL = """
ipv6 address {addr} link-local
"""

CONFIG_IPV6_LINK_LOCAL_VLAN = """
int {port}.{vlan}
""" + CONFIG_IPV6_LINK_LOCAL.format(addr="FE80::1")

STATIC_ROUTES = {
    "IPV4_NEXT_HOP": """
ip route {net_addr} {subnet_mask} {next_hop} {ad}
""",
    "IPV4_DIRECTLY_CONNECTED": """
ip route {net_addr} {subnet_mask} {intf} {ad}
""",
    "IPV4_FULLY_SPECIFIED": """
ip route {net_addr} {subnet_mask} {intf} {next_hop} {ad}
""",
    "IPV6_NEXT_HOP": """
ipv6 route {net_addr} {next_hop} {ad}
""",
    "IPV6_DIRECTLY_CONNECTED": """
ipv6 route {net_addr} {intf} {ad}
""",
    "IPV6_FULLY_SPECIFIED": """
ipv6 route {net_addr} {intf} {next_hop} {ad}
""",
}
