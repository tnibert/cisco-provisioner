from templates import *
from vlan import Vlan, NativeVlan
from typing import List, Union
from functools import reduce

class Ports:
    """
    Group of physical network interface, not TCP/UDP port
    """
    def __init__(self, ports):
        self.ports = ports

    def provision(self) -> str:
        return "!UNIMPLEMENTED\n"

class UnusedPorts(Ports):
    def __init__(self, ports):
        super().__init__(ports)

    def provision(self) -> str:
        return CONFIG_UNUSED_PORTS.format(ports=self.ports)

class TrunkPorts(Ports):
    def __init__(self, ports, vlans: List[Union[Vlan|NativeVlan]]):
        super().__init__(ports)
        self.vlans = vlans

    def provision(self) -> str:
        regular = reduce(lambda a,x: a+","+x,
                         map(lambda v: str(v.get_number()), self.vlans))
        native = reduce(lambda a,x: a+x,
                        map(lambda v: v.provision_switch_trunk(),
                            filter(lambda v: isinstance(v, NativeVlan), self.vlans)))
        return CONFIG_TRUNK_PORTS.format(ports=self.ports,
                                         allowed=CONFIG_TRUNK_REGULAR.format(number=regular) + native)

class AccessPorts(Ports):
    def __init__(self, ports, access_vlan):
        super().__init__(ports)
        self.access_vlan = access_vlan

    def provision(self) -> str:
        return CONFIG_ACCESS_PORTS.format(ports=self.ports, access_vlan=self.access_vlan)

class EtherChannelPorts(Ports):
    def __init__(self, ports, chan_num):
        super().__init__(ports)
        self.chan_num = chan_num

    def provision(self) -> str:
        return CONFIG_ETHERCHANNEL_PORTS.format(ports=self.ports, chan_num=self.chan_num)
