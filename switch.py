from functools import reduce
from templates import *

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
