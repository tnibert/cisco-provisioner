from functools import reduce
from templates import *
from device import Device
from vlan import Vlan
from ports import Ports
from typing import List

class Switch(Device):
    def __init__(self, hostname, vlan: Vlan, ip, port_configs: List[Ports]):
        super().__init__(hostname, 15)
        self.vlan = vlan
        self.ip = ip
        self.port_configs = port_configs

    def provision_ssh(self) -> str:
        if self.vlan is not None:
            return SWITCH_SVI_SSH.format(vlan=self.vlan.number, ip=self.ip, subnet=self.vlan.mask, gateway=self.vlan.gateway, vty_max=self.vty_max)
        else:
            return ""

    def provision_switch_ports(self):
        return reduce(lambda a, x: a + x, [p.provision_switch_ports() for p in self.port_configs])

    def all_provisioning(self) -> str:
        return self.provision_basic() + self.provision_ssh() + self.provision_switch_ports()
