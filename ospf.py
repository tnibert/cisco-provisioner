from functools import reduce
from typing import List

from ip import IPAddress
from provisionable import Provisionable, provision_group
from templates.ospf import ospf_setup, network, passive_interface, v2_init, v3_init, ipv6_interface, set_asbr, \
    set_hello_ival
from templates.router import INTERFACE_BLOCK

"""
todo: cost, bandwidth, and reference bandwidth modification is not yet implemented
"""

DEFAULT_HELLO_INTERVAL = 10


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


class OSPFInterface(Provisionable):
    def __init__(self, intf: str, hello_interval=DEFAULT_HELLO_INTERVAL):
        self.intf = intf
        self.hello_interval=hello_interval

    def provision(self):
        return INTERFACE_BLOCK.format(
            intf=self.intf,
            body=set_hello_ival.format(seconds=self.hello_interval)
        ) if self.hello_interval != DEFAULT_HELLO_INTERVAL else ""


class OSPFv3Interface(OSPFInterface):
    def __init__(self, intf_name, area=0, process_id=None, hello_interval=DEFAULT_HELLO_INTERVAL):
        super.__init__(intf_name, hello_interval)
        self.area = area
        self.process_id = process_id

    def set_process_id(self, process_id) -> OSPFv3Interface:
        self.process_id = process_id
        return self

    def provision(self):
        return INTERFACE_BLOCK.format(
            intf=self.intf,
            body=ipv6_interface.format(process_id=self.process_id,
                                       area_id=self.area) + \
                 (set_hello_ival.format(seconds=self.hello_interval) if self.hello_interval != DEFAULT_HELLO_INTERVAL else "")
        )


class OSPF(Provisionable):
    """
    NB: Don't initialize this directly, use one of the versioned child classes.
    """
    def __init__(self, passive_interfaces: List[str], router_id, process_id, asbr=False):
        self.passive_interfaces = passive_interfaces if passive_interfaces is not None else []
        self.router_id = router_id
        self.process_id = process_id
        self.asbr = asbr


class OSPFv2(OSPF):
    def __init__(self,
                 networks: List[OSPFv2Network],
                 passive_interfaces: List[str],
                 router_id,
                 process_id,
                 interfaces: List[OSPFInterface]=None,
                 asbr=False):
        super().__init__(passive_interfaces, router_id, process_id, asbr)
        self.networks = networks if networks is not None else []
        self.interfaces = interfaces if interfaces is not None else []

    def provision(self):
        return ospf_setup.format(version_init=v2_init.format(process_id=self.process_id),
                                 router_id=self.router_id,
                                 networks=provision_group(self.networks),
                                 passive_interfaces=reduce(lambda a, x: a + x,
                                                           map(lambda p: passive_interface.format(intf=p),
                                                               self.passive_interfaces), ""),
                                 asbr=set_asbr if self.asbr else ""
                                 ) + provision_group(self.interfaces)


class OSPFv3(OSPF):
    def __init__(self,
                 interfaces: List[OSPFv3Interface],
                 passive_interfaces: List[str],
                 router_id,
                 process_id,
                 asbr=False):
        super().__init__(passive_interfaces, router_id, process_id, asbr)
        self.interfaces = list(map(lambda i: i.set_process_id(process_id), interfaces))

    def provision(self):
        return ospf_setup.format(
                          version_init=v3_init.format(process_id=self.process_id),
                          router_id=self.router_id,
                          networks="",
                          passive_interfaces=reduce(lambda a, x: a + x,
                                                    map(lambda p: passive_interface.format(intf=p),
                                                        self.passive_interfaces), ""),
                          asbr=set_asbr if self.asbr else ""
                          ) + provision_group(self.interfaces)
