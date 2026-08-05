from router import Router, Port, RouterOnAStickPort, IPv4LoopbackPort
from routes import StaticIPv4Route
from switch import Switch
from ports import *
from vlan import Vlan, NativeVlan
from ip import IPAddress
from dhcp import DHCPServer, DHCPPool, DHCPRelay

DOMAIN = "cisco.com"

hq_s000_ipv4 = IPAddress("172.16.30.1", 30)
hq_g00_ipv4 = IPAddress("192.168.100.1", 24)
hq_lo0_ipv4 = IPAddress("209.165.200.1", 24)
branch_s000_ipv4 = IPAddress("172.16.30.2", 30)

vlan_10_gw_ipv4 = IPAddress("192.168.10.1", 24)
vlan_20_gw_ipv4 = IPAddress("192.168.20.1", 24)
vlan_99_gw_ipv4 = IPAddress("192.168.99.1", 24)

vlan_10_net_ipv4 = IPAddress("192.168.10.0", 24)
vlan_20_net_ipv4 = IPAddress("192.168.20.0", 24)
vlan_99_net_ipv4 = IPAddress("192.168.99.0", 24)
lan_1_net_ipv4 = IPAddress("192.168.100.0", hq_g00_ipv4.get_mask_len())

switch_ipv4 = IPAddress("192.168.99.11", vlan_99_gw_ipv4.get_mask_len())
default_route_net_ipv4 = IPAddress("0.0.0.0", 0)

dhcp_relay = DHCPRelay(hq_s000_ipv4)


vlans = {
    10: Vlan("Sales", 10, vlan_10_gw_ipv4, "g0/0", dhcp=True),
    20: Vlan("IT", 20, vlan_20_gw_ipv4, "g0/0", dhcp=True),
    99: Vlan("Management", 99, vlan_99_gw_ipv4, "g0/0"),
    555: Vlan("Parking_Lot", 555),
    1000: NativeVlan(1000)
}

devices = {
    "S1": Switch("S1", vlans[99], switch_ipv4,
                 list(vlans.values()),
                 [
                     TrunkPorts("f0/1", [vlans[10], vlans[20], vlans[99], vlans[1000]]),
                     AccessPorts("f0/6", 10),
                     AccessPorts("f0/18", 20),
                     UnusedPorts("f0/2-5,f0/7-17,f0/19-24,g0/1-2"),
                 ]),
    "BRANCH": Router("BRANCH",
                     [
                         RouterOnAStickPort("g0/0", [vlans[10], vlans[20], vlans[99], vlans[1000]], dhcp_relay),
                         Port("s0/0/0", branch_s000_ipv4, None)
                     ],
                     [
                         StaticIPv4Route(default_route_net_ipv4, hq_s000_ipv4, "s0/0/0"),
                     ]),
    "HQ": Router("HQ",
                 [
                     Port("g0/0", hq_g00_ipv4, None),
                     Port("s0/0/0", hq_s000_ipv4, None, dce=True),
                     IPv4LoopbackPort(hq_lo0_ipv4, 0)
                 ],
                 [
                     StaticIPv4Route(vlan_10_net_ipv4, branch_s000_ipv4),
                     StaticIPv4Route(vlan_20_net_ipv4, branch_s000_ipv4),
                     StaticIPv4Route(vlan_99_net_ipv4, branch_s000_ipv4),
                 ],
                 DHCPServer([
                     hq_g00_ipv4,
                     IPAddress("192.168.100.2", hq_g00_ipv4.get_mask_len()),
                     IPAddress("192.168.100.3", hq_g00_ipv4.get_mask_len()),
                     IPAddress("192.168.100.4", hq_g00_ipv4.get_mask_len()),
                     IPAddress("192.168.100.5", hq_g00_ipv4.get_mask_len()),
                     vlan_10_gw_ipv4,
                     IPAddress("192.168.10.2", vlan_10_gw_ipv4.get_mask_len()),
                     IPAddress("192.168.10.3", vlan_10_gw_ipv4.get_mask_len()),
                     IPAddress("192.168.10.4", vlan_10_gw_ipv4.get_mask_len()),
                     IPAddress("192.168.10.5", vlan_10_gw_ipv4.get_mask_len()),
                     vlan_20_gw_ipv4,
                     IPAddress("192.168.20.2", vlan_20_gw_ipv4.get_mask_len()),
                     IPAddress("192.168.20.3", vlan_20_gw_ipv4.get_mask_len()),
                     IPAddress("192.168.20.4", vlan_20_gw_ipv4.get_mask_len()),
                     IPAddress("192.168.20.5", vlan_20_gw_ipv4.get_mask_len())
                 ], [
                     DHCPPool("LAN1", lan_1_net_ipv4, hq_g00_ipv4, domain_name=DOMAIN),
                     DHCPPool("LAN10", vlan_10_net_ipv4, vlan_10_gw_ipv4, domain_name=DOMAIN),
                     DHCPPool("LAN20", vlan_20_net_ipv4, vlan_20_gw_ipv4, domain_name=DOMAIN),
                 ]))
}