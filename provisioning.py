import sys

from router import Router, Port, RouterOnAStickPort
from routes import StaticIPv4Route
from switch import Switch
from ports import *
from vlan import Vlan, NativeVlan
from ip import IPAddress

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

switch_ipv4 = IPAddress("192.168.99.11", vlan_99_gw_ipv4.get_mask_len())
default_route_net_ipv4 = IPAddress("0.0.0.0", 0)

format_octet_binary = lambda n: '{0:08b}'.format(n)

vlans = {
    10: Vlan("Sales", 10, vlan_10_gw_ipv4, "g0/0"),
    20: Vlan("IT", 20, vlan_20_gw_ipv4, "g0/0"),
    99: Vlan("Management", 99, vlan_99_gw_ipv4, "g0/0"),
    555: Vlan("Parking_Lot", 555),
    1000: NativeVlan(1000, "g0/0")
}

devices = {
    "S1": Switch("S1", vlans[99], switch_ipv4,
                 list(vlans.values()),
                 [
                     TrunkPorts("f0/1", [vlans[10], vlans[20], vlans[99], vlans[1000]]),
                     AccessPorts("f0/6,f0/18", 99),
                     UnusedPorts("f0/2-5,f0/7-17,f0/19-24,g0/1-2"),
                 ]),
    "BRANCH": Router("BRANCH",
                     [
                         RouterOnAStickPort("g0/0", [vlans[10], vlans[20], vlans[99], vlans[1000]]),
                         Port("s0/0/0", branch_s000_ipv4, None)
                     ],
                     [
                         StaticIPv4Route(default_route_net_ipv4, hq_s000_ipv4, "s0/0/0"),
                     ]),
    "HQ": Router("HQ",
                 [
                     Port("g0/0", hq_g00_ipv4, None),
                     Port("s0/0/0", hq_s000_ipv4, None, dce=True)
                 ],
                 [
                     StaticIPv4Route(vlan_10_net_ipv4, branch_s000_ipv4),
                     StaticIPv4Route(vlan_20_net_ipv4, branch_s000_ipv4),
                     StaticIPv4Route(vlan_99_net_ipv4, branch_s000_ipv4),
                 ])
}

if __name__=='__main__':
    """
    generate provisioning commands
    """
    if len(sys.argv) > 1:
        # provision specific device
        print(devices[sys.argv[1]].provision())
    else:
        # all
        for k,v in devices.items():
            config = v.provision()
            print(f"-----{k}-----")
            print(config)
