from functools import reduce

from ip import IPAddress
from templates import *
from device import Device
from vlan import Vlan
from ports import Ports
from typing import List

class Switch(Device):
    def __init__(self, hostname, vlan: Vlan, ip: IPAddress, port_configs: List[Ports]):
        super().__init__(hostname, 15)
        self.vlan = vlan
        self.ip = ip
        self.port_configs = port_configs

    def provision_ssh(self) -> str:
        if None in (self.vlan, self.ip):
            return ""
        else:
            return SWITCH_SVI_SSH.format(vlan=self.vlan.number,
                                         ip=self.ip.get_ip_addr(),
                                         subnet=self.vlan.ipv4_gateway.get_mask(),
                                         gateway=self.vlan.ipv4_gateway.get_ip_addr(),
                                         vty_max=self.vty_max)

    def provision_switch_ports(self):
        return reduce(lambda a, x: a + x, [p.provision() for p in self.port_configs])

    def provision(self) -> str:
        return self.provision_basic() + self.provision_ssh() + self.provision_switch_ports()
