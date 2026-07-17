import sys

from vlan import Vlan, NativeVlan
from router import Router
from switch import Switch
from ports import *

def print_power_of_2():
    for i in range(0, 10):
        print(f"{2**i} : {i}")

lab1_vlans = {
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

lab1_devices = {
    "S1": Switch("S1", lab1_vlans[99], "132.234.242.50", 28, "132.234.242.49",
                 [
                     TrunkPorts("f0/1"),
                     EtherChannelPorts("f0/2-3", 1),
                     EtherChannelPorts("f0/4-5", 2),
                     UnusedPorts("f0/6-24,g0/1-2"),
                 ]),
    "S2": Switch("S2", lab1_vlans[99], "132.234.242.51", 28, "132.234.242.49",
                 [
                     TrunkPorts("f0/3-5"),
                     EtherChannelPorts("f0/1-2", 1),
                     UnusedPorts("f0/6-24,g0/1-2"),
                 ]),
    "S3": Switch("S3", lab1_vlans[99], "132.234.242.52", 28, "132.234.242.49",
                 [
                     TrunkPorts("f0/3-5"),
                     EtherChannelPorts("f0/1-2", 2),
                     UnusedPorts("f0/6-24,g0/1-2"),
                 ]),
    "S4": Switch("S4", lab1_vlans[99], "132.234.242.53", 28, "132.234.242.49",
                 [
                     AccessPorts("f0/6", 10),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S5": Switch("S5", lab1_vlans[99], "132.234.242.54", 28, "132.234.242.49",
                 [
                     AccessPorts("f0/6", 20),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S6": Switch("S6", lab1_vlans[99], "132.234.242.55", 28, "132.234.242.49",
                 [
                     AccessPorts("f0/6", 30),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S7": Switch("S7", lab1_vlans[100], "132.234.242.66", 29, "132.234.242.65",
                 [
                     AccessPorts("f0/6", 40),
                     TrunkPorts("f0/1-3"),
                     UnusedPorts("f0/4-5,f0/7-24,g0/1-2"),
                 ]),
    "S8": Switch("S8", lab1_vlans[100], "132.234.242.67", 29, "132.234.242.65",
                 [
                     AccessPorts("f0/6", 50),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "S9": Switch("S9", lab1_vlans[100], "132.234.242.68", 29, "132.234.242.65",
                 [
                     AccessPorts("f0/6", 60),
                     TrunkPorts("f0/1-2"),
                     UnusedPorts("f0/3-5,f0/7-24,g0/1-2"),
                 ]),
    "Router": Router(lab1_vlans.values())
}

if __name__=='__main__':
    """
    generate provisioning commands
    """
    if len(sys.argv) > 1:
        print(lab1_devices[sys.argv[1]].all_provisioning())
        #print(s.provision_basic_switch())
        #print(s.provision_ssh())
        #for p in s.port_configs:
        #    print(p.provision_switch_ports())
    else:
        # all
        for k,v in lab1_devices.items():
            print(f"-----{k}-----")
            print(v.all_provisioning())
            print("--------------\n")
