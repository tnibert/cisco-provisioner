BASIC_CONFIG = """
hostname {host}
no ip domain-lookup
enable secret class
line console 0
password cisco
login
logging synchronous
exit
line vty 0 {vty_max}
password cisco
login
logging synchronous
exit
service password-encryption
banner motd $ Authorized Access Only! $
ipv6 unicast-routing
"""

CONFIG_ROUTER_PORT = """
interface {intf}
ip address {ipv4} {subnet_mask}
{additional}
no shutdown
"""

CONFIG_IPV6_PORT = """
ipv6 address {ipv6}
"""

DCE = """
clock rate 128000
"""

SWITCH_SVI_SSH = """
! SVI interface
int vlan {vlan}
ip address {ip} {subnet}
no shut
exit

ip default-gateway {gateway}

! setup ssh - router vty 0 4, switch vty 0 15
ip domain-name cisco.com
crypto key generate rsa general-keys modulus 1024
username admin secret cisco
line vty 0 {vty_max}
transport input ssh
login local
exit
ip ssh version 2
"""

CONFIG_SWITCH_VLAN = """
vlan {number}
name {name}
"""

CONFIG_LOOPBACK_IPV4 = """
interface loopback {number}
ip address {addr} {mask}
exit
"""

CONFIG_ACCESS_PORTS = """
int range {ports}
switchport mode access
switchport access vlan {access_vlan}
! portfast and BPDU
spanning-tree portfast
spanning-tree bpduguard enable

! secure access ports
switchport port-security
switchport port-security max 1
switchport port-security mac-address sticky
switchport port-security violation shutdown
no shut
exit
"""

CONFIG_TRUNK_PORTS = """
int range {ports}
switchport mode trunk
{allowed}
! secure trunk ports
switchport nonegotiate
exit
"""

CONFIG_TRUNK_NATIVE = """
switchport trunk native vlan {number}
"""

# todo: need to specify multiple in one go?
CONFIG_TRUNK_REGULAR = """
switchport trunk allow vlan {number}
"""

CONFIG_UNUSED_PORTS = """
! disable unused ports
int range {ports}
switchport mode access
switchport access vlan 555
shut
exit
"""

CONFIG_ETHERCHANNEL_PORTS = """
! etherchannel
interface range {ports}
channel-group {chan_num} mode desirable
exit
interface port-channel {chan_num}
switchport mode trunk
switchport trunk allow vlan 10,20,30,40,50,60,99,100,1000
switchport trunk native vlan 1000
exit
show interfaces port-channel {chan_num}
show etherchannel summary
"""

CONFIG_ROUTER_ON_A_STICK_CLOSE = """
int {port}
no shut
"""

CONFIG_ROUTER_ON_A_STICK_BLOCK = """
int {port}.{vlan}
encapsulation dot1q {vlan}
ip address {gw} {mask}
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
