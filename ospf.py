from functools import reduce
from typing import List

from ip import IPAddress
from provisionable import Provisionable, provision_group
from templates.ospf import ospf_setup, network, passive_interface, v2_init, v3_init, ipv6_interface
from templates.router import INTERFACE_BLOCK

"""
todo: cost, bandwidth, and reference bandwidth modification is not yet implemented
"""

class OSPFv2Network(Provisionable):
    def __init__(self, net_addr: IPAddress, area=0):
        self.net_addr = net_addr
        self.area = area

    def provision(self):
        return network.format(
            net_addr=self.net_addr.get_ip_addr(),
            wildcard_mask=self.net_addr.get_wildcard_mask(),
            area_id=self.area
        )


class OSPFv3Interface(Provisionable):
    def __init__(self, intf_name, area=0, process_id=None):
        self.intf = intf_name
        self.area = area
        self.process_id = process_id

    def set_process_id(self, process_id) -> OSPFv3Interface:
        self.process_id = process_id
        return self

    def provision(self):
        return INTERFACE_BLOCK.format(
            intf=self.intf,
            body=ipv6_interface.format(process_id=self.process_id,
                                       area_id=self.area)
        )


class OSPF(Provisionable):
    """
    NB: Don't initialize this directly, use one of the versioned child classes.
    """
    def __init__(self, passive_interfaces: List[str], router_id, process_id):
        self.passive_interfaces = passive_interfaces if passive_interfaces is not None else []
        self.router_id = router_id
        self.process_id = process_id


class OSPFv2(OSPF):
    def __init__(self, networks: List[OSPFv2Network], passive_interfaces: List[str], router_id, process_id):
        super().__init__(passive_interfaces, router_id, process_id)
        self.networks = networks if networks is not None else []

    def provision(self):
        return ospf_setup.format(version_init=v2_init.format(process_id=self.process_id),
                                 router_id=self.router_id,
                                 networks=provision_group(self.networks),
                                 passive_interfaces=reduce(lambda a, x: a + x,
                                                           map(lambda p: passive_interface.format(intf=p),
                                                               self.passive_interfaces), ""),
                                 )


class OSPFv3(OSPF):
    def __init__(self, interfaces: List[OSPFv3Interface], passive_interfaces: List[str], router_id, process_id):
        super().__init__(passive_interfaces, router_id, process_id)
        self.interfaces = list(map(lambda i: i.set_process_id(process_id), interfaces))

    def provision(self):
        return ospf_setup.format(
                          version_init=v3_init.format(process_id=self.process_id),
                          router_id=self.router_id,
                          networks="",
                          passive_interfaces=reduce(lambda a, x: a + x,
                                                    map(lambda p: passive_interface.format(intf=p),
                                                        self.passive_interfaces), ""),
                          ) + provision_group(self.interfaces)
