from functools import reduce

from ip import IPAddress
from templates import *
from device import Device
from vlan import Vlan, NativeVlan
from ports import Ports, TrunkPorts
from typing import List, Union

class Switch(Device):
    def __init__(self, hostname, access_vlan: Vlan, ip: IPAddress, vlans: List[Union[Vlan,NativeVlan]], port_configs: List[Ports]):
        super().__init__(hostname, 15)
        self.access_vlan = access_vlan
        self.ip = ip
        self.port_configs = port_configs
        self.vlans = vlans

    def provision_ssh(self) -> str:
        if None in (self.access_vlan, self.ip):
            return ""
        else:
            return SWITCH_SVI_SSH.format(vlan=self.access_vlan.number,
                                         ip=self.ip.get_ip_addr(),
                                         subnet=self.access_vlan.ipv4_gateway.get_mask(),
                                         gateway=self.access_vlan.ipv4_gateway.get_ip_addr(),
                                         vty_max=self.vty_max)

    def provision_switch_ports(self):
        return reduce(lambda a, x: a + x, [p.provision() for p in self.port_configs])

    def provision_switch_vlans(self):
        return reduce(lambda a, x: a + x, [v.provision_switch_vlan() for v in self.vlans])

    def provision(self) -> str:
        return self.provision_basic() + self.provision_switch_vlans() + self.provision_ssh() + self.provision_switch_ports()
