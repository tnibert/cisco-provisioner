import socket
import struct
import sys
from functools import reduce

def cidr_prefix_to_netmask(net_bits):
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask

def print_power_of_2():
    for i in range(0, 10):
        print(f"{2**i} : {i}")

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
exit
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

def create_router_on_a_stick():
    pass

class Ports:
    """
    Group of physical network interface, not TCP/UDP port
    """
    def __init__(self, ports):
        self.ports = ports

    def provision_switch_ports(self) -> str:
        return "!UNIMPLEMENTED\n"

class UnusedPorts(Ports):
    def __init__(self, ports):
        super().__init__(ports)

    def provision_switch_ports(self) -> str:
        return CONFIG_UNUSED_PORTS.format(ports=self.ports)

class TrunkPorts(Ports):
    def __init__(self, ports):
        super().__init__(ports)

    def provision_switch_ports(self) -> str:
        return CONFIG_TRUNK_PORTS.format(ports=self.ports)

class AccessPorts(Ports):
    def __init__(self, ports, access_vlan):
        super().__init__(ports)
        self.access_vlan = access_vlan

    def provision_switch_ports(self) -> str:
        return CONFIG_ACCESS_PORTS.format(ports=self.ports, access_vlan=self.access_vlan)

class EtherChannelPorts(Ports):
    def __init__(self, ports, chan_num):
        super().__init__(ports)
        self.chan_num = chan_num

    def provision_switch_ports(self) -> str:
        return CONFIG_ETHERCHANNEL_PORTS.format(ports=self.ports, chan_num=self.chan_num)

class Vlan:
    def __init__(self, number, gw, mask_prefix, router_port, ipv6=None):
        self.number = number
        self.gateway = gw
        self.ipv6_gateway = ipv6
        self.mask = cidr_prefix_to_netmask(mask_prefix)
        self.router_port = router_port

    def provision_router_on_a_stick(self) -> str:
        return CONFIG_ROUTER_ON_A_STICK_BLOCK.format(vlan=self.number, gw=self.gateway, mask=self.mask, port=self.router_port, ipv6=self.ipv6_gateway)

    def provision_ipv6(self) -> str:
        return CONFIG_IPV6_BLOCK.format(port=self.router_port, vlan=self.number, ipv6=self.ipv6_gateway) if self.ipv6_gateway is not None else ""

class NativeVlan:
    def __init__(self, number, router_port):
        self.number = number
        self.router_port = router_port

    def provision_router_on_a_stick(self) -> str:
        return CONFIG_NATIVE_ROUTER_ON_A_STICK_BLOCK.format(vlan=self.number, port=self.router_port)

    def provision_ipv6(self) -> str:
        return ""

class Switch:
    def __init__(self, hostname, vlan: Vlan, ip, mask_prefix, gw, port_configs: List[Ports]):
        self.hostname = hostname
        self.vlan = vlan
        self.ip = ip
        self.vty_max = 15
        self.port_configs = port_configs

    def provision_ssh(self) -> str:
        return SWITCH_SVI_SSH.format(vlan=self.vlan.number, ip=self.ip, subnet=self.vlan.mask, gateway=self.vlan.gateway, vty_max=self.vty_max)

    def provision_basic_switch(self) -> str:
        return BASIC_CONFIG.format(host=self.hostname, vty_max=self.vty_max)

    def all_provisioning(self) -> str:
        return self.provision_basic_switch() + self.provision_ssh() + reduce(lambda a, x: a + x, [p.provision_switch_ports() for p in self.port_configs])

class Router:
    def __init__(self, vlans: List[Vlan]):
        self.vlans = vlans

    def provision_router_on_a_stick(self) -> str:
        provisioning = reduce(lambda a, x: a + x,
                          map(lambda v: v.provision_router_on_a_stick(),
                              self.vlans)) \
                        + CONFIG_ROUTER_ON_A_STICK_CLOSE.format(port="G0/0") \
                        + CONFIG_ROUTER_ON_A_STICK_CLOSE.format(port="G0/1")

        return "configure terminal\n" + provisioning + "exit\nexit\n"

    def provision_ipv6(self) -> str:
        return reduce(lambda a, x: a + x,
                  map(lambda v: v.provision_ipv6(),
                      self.vlans))

    def all_provisioning(self) -> str:
        return self.provision_router_on_a_stick() + self.provision_ipv6()

my_vlans = {
    10: Vlan(10, "132.234.241.1", 25, "G0/0", "2001:DB8:CAFE:10::1/64"),
    20: Vlan(20, "132.234.240.1", 24, "G0/0", "2001:DB8:CAFE:20::1/64"),
    30: Vlan(30, "132.234.241.193", 26, "G0/0", "2001:DB8:CAFE:30::1/64"),
    40: Vlan(40, "132.234.242.1", 27, "G0/1", "2001:DB8:CAFE:40::1/64"),
    50: Vlan(50, "132.234.241.129", 26, "G0/1", "2001:DB8:CAFE:50::1/64"),
    60: Vlan(60, "132.234.242.33", 28, "G0/1", "2001:DB8:CAFE:60::1/64"),
    99: Vlan(99, "132.234.242.49", 28, "G0/0"),
    100: Vlan(100, "132.234.242.65", 29, "G0/1"),
    1000: NativeVlan(1000, "G0/0")
}

devices = {
    "S1": Switch("S1", my_vlans[99], "132.234.242.50", 28, "132.234.242.49",
                 [
                     TrunkPorts("f0/1"),
                     EtherChannelPorts("f0/2-3", 1),
                     EtherChannelPorts("f0/4-5", 2),
                     UnusedPorts("f0/6-24,g0/1-2"),
                 ]),
    "S2": Switch("S2", my_vlans[99], "132.234.242.51", 28, "132.234.242.49",
                 [
                     TrunkPorts("f0/3-5"),
                     EtherChannelPorts("f0/1-2", 1),
                     UnusedPorts("f0/6-24,g0/1-2"),
                 ]),
    "S3": Switch("S3", my_vlans[99], "132.234.242.52", 28, "132.234.242.49",
                 [
                     TrunkPorts("f0/3-5"),
                     EtherChannelPorts("f0/1-2", 2),
                     UnusedPorts("f0/6-24,g0/1-2"),
                 ]),
    "S4": Switch("S4", my_vlans[99], "132.234.242.53", 28, "132.234.242.49",
                 [
                     AccessPorts("f0/6", 10),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S5": Switch("S5", my_vlans[99], "132.234.242.54", 28, "132.234.242.49",
                 [
                     AccessPorts("f0/6", 20),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S6": Switch("S6", my_vlans[99], "132.234.242.55", 28, "132.234.242.49",
                 [
                     AccessPorts("f0/6", 30),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S7": Switch("S7", my_vlans[100], "132.234.242.66", 29, "132.234.242.65",
                 [
                     AccessPorts("f0/6", 40),
                     TrunkPorts("f0/1-3"),
                     UnusedPorts("f0/4-5,f0/7-24,g0/1-2"),
                 ]),
    "S8": Switch("S8", my_vlans[100], "132.234.242.67", 29, "132.234.242.65",
                 [
                     AccessPorts("f0/6", 50),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S9": Switch("S9", my_vlans[100], "132.234.242.68", 29, "132.234.242.65",
                 [
                     AccessPorts("f0/6", 60),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "Router": Router(my_vlans.values())
}

if __name__=='__main__':
    """
    generate provisioning commands
    """
    if len(sys.argv) > 1:
        s = devices[sys.argv[1]]
        print(s.provision_basic_switch())
        print(s.provision_ssh())
        for p in s.port_configs:
            print(p.provision_switch_ports())

    else:
        # all
        for k,v in devices.items():
            print(f"-----{k}-----")
            print(v.all_provisioning())
            print("--------------\n")
