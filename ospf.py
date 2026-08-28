from functools import reduce
from typing import List

from ip import IPAddress
from provisionable import Provisionable
from templates.ospf import ospf_setup, network, passive_interface, v2_init, v3_init, ipv6_interface
from templates.router import INTERFACE_BLOCK

"""
todo: cost, bandwidth, and reference bandwidth modification is not yet implemented
"""

class OSPF(Provisionable):
    """
    NB: Don't initialize this directly, use one of the versioned child classes.
    """
    def __init__(self, passive_interfaces: List[str], router_id, process_id):
        self.passive_interfaces = passive_interfaces if passive_interfaces is not None else []
        self.router_id = router_id
        self.process_id = process_id


class OSPFv2(OSPF):
    def __init__(self, networks: List[IPAddress], passive_interfaces: List[str], router_id, process_id):
        super().__init__(passive_interfaces, router_id, process_id)
        self.networks = networks if networks is not None else []

    def provision(self):
        return ospf_setup.format(version_init=v2_init.format(process_id=self.process_id),
                                 router_id=self.router_id,
                                 networks=reduce(lambda a, x: a + x,
                                                 map(lambda n: network.format(
                                                     net_addr=n.get_ip_addr(),
                                                     wildcard_mask=n.get_wildcard_mask(),
                                                     area_id=0
                                                 ),
                                                     self.networks), ""),
                                 passive_interfaces=reduce(lambda a, x: a + x,
                                                           map(lambda p: passive_interface.format(intf=p),
                                                               self.passive_interfaces), ""),
                                 )

class OSPFv3(OSPF):
    def __init__(self, interfaces: List[str], passive_interfaces: List[str], router_id, process_id):
        super().__init__(passive_interfaces, router_id, process_id)
        self.interfaces = interfaces

    def provision_interfaces(self) -> str:
        return reduce(lambda a,x: a+x,
                      map(lambda i: INTERFACE_BLOCK.format(intf=i,
                                                           body=ipv6_interface.format(process_id=self.process_id,
                                                                                      area_id=0)),
                          self.interfaces),
                      "")

    def provision(self):
        return ospf_setup.format(version_init=v3_init.format(process_id=self.process_id),
                          router_id=self.router_id,
                          networks="",
                          passive_interfaces=reduce(lambda a, x: a + x,
                                                    map(lambda p: passive_interface.format(intf=p),
                                                        self.passive_interfaces), ""),
                          ) + self.provision_interfaces()
