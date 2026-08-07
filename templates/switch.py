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

CONFIG_ACCESS_PORTS = """
int range {ports}
switchport mode access
{access_vlan_clause}
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

CONFIG_ACCESS_VLAN = """
switchport access vlan {access_vlan}
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

CONFIG_TRUNK_REGULAR = """
switchport trunk allow vlan {number}
"""

# todo: pass in parking lot vlan
CONFIG_UNUSED_PORTS = """
! disable unused ports
int range {ports}
switchport mode access
switchport access vlan 555
shut
exit
"""

# todo: unify with other trunk config and remove hard coded vlans
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
