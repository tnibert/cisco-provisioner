from provisionable import Provisionable
from templates.switch import (CONFIG_UNUSED_PORTS, CONFIG_TRUNK_PORTS, CONFIG_TRUNK_REGULAR, CONFIG_ACCESS_PORTS,
                              CONFIG_ACCESS_VLAN, CONFIG_ETHERCHANNEL_PORTS)
from utils import partition
from vlan import Vlan, NativeVlan
from typing import List, Union
from functools import reduce

"""
Switch ports, not router ports
"""

class Ports(Provisionable):
    """
    Group of physical network interface, not TCP/UDP port
    """
    def __init__(self, ports):
        self.ports = ports

class UnusedPorts(Ports):
    def __init__(self, ports, parking_lot_vlan: Vlan=Vlan("Parking_Lot", 555)):
        super().__init__(ports)
        self.parking_lot_vlan = parking_lot_vlan

    def provision(self) -> str:
        return CONFIG_UNUSED_PORTS.format(ports=self.ports, parking_lot=self.parking_lot_vlan.get_number())

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
    def __init__(self, ports, access_vlan: Vlan=None):
        super().__init__(ports)
        self.access_vlan = access_vlan

    def provision(self) -> str:
        return CONFIG_ACCESS_PORTS.format(ports=self.ports,
                                          access_vlan_clause=CONFIG_ACCESS_VLAN.format(
                                              access_vlan=self.access_vlan.get_number()
                                          ) if self.access_vlan is not None else "")

class EtherChannelPorts(Ports):
    def __init__(self, ports, chan_num, vlans: List[Union[Vlan|NativeVlan]]):
        super().__init__(ports)
        self.chan_num = chan_num
        self.vlans = vlans

    def provision(self) -> str:
        regular_vlans, native_vlans = partition(lambda v: not isinstance(v, NativeVlan), self.vlans)
        regular_vlans_str = reduce(lambda a,x: a+","+x, map(lambda v: str(v.get_number()), regular_vlans))
        native_vlan = list(map(lambda v: str(v.get_number()), native_vlans))[0]
        return CONFIG_ETHERCHANNEL_PORTS.format(ports=self.ports,
                                                chan_num=self.chan_num,
                                                vlans=regular_vlans_str,
                                                native_vlan=native_vlan)
