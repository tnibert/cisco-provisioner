BASIC_CONFIG = """
configure terminal
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
exit
"""

CONFIG_ROUTER_PORT = """
interface {intf}
ip address {ipv4} {subnet_mask}
ipv6 address {ipv6}
{additional}
no shutdown
"""

DCE = """
clock rate 128000
"""

SWITCH_SVI_SSH = """
configure terminal
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
exit

show ip ssh
show ssh
"""

CONFIG_SWITCH_UNIVERSAL_VLANS = """
configure terminal
vlan 10
name IT
vlan 20
name Sales
vlan 30
name Operation
vlan 40
name HR
vlan 50
name Marketing
vlan 60
name Finance
vlan 99
name OvalManagement
vlan 100
name SquareManagement
vlan 555
name Parking_Lot
vlan 1000
name Native
exit
exit
"""

CONFIG_ACCESS_PORTS = """
configure terminal
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
exit
"""

CONFIG_TRUNK_PORTS = """
configure terminal
int range {ports}
switchport mode trunk
switchport trunk native vlan 1000
switchport trunk allow vlan 10,20,30,40,50,60,99,100,1000
! secure trunk ports
switchport nonegotiate
exit
exit
"""

CONFIG_UNUSED_PORTS = """
configure terminal
! disable unused ports
int range {ports}
switchport mode access
switchport access vlan 555
shut
exit
exit
"""

CONFIG_ETHERCHANNEL_PORTS = """
! etherchannel
configure terminal
interface range {ports}
channel-group {chan_num} mode desirable
exit
interface port-channel {chan_num}
switchport mode trunk
switchport trunk allow vlan 10,20,30,40,50,60,99,100,1000
switchport trunk native vlan 1000
exit
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
ipv6 address {ipv6}
"""

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
