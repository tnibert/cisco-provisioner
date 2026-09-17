from functools import reduce
from typing import List

from ip import IPAddress, IPv4Address, IPv6Address
from provisionable import Provisionable, provision_group
from templates.ospf import ospf_setup, network, passive_interface, v2_init, v3_init, ipv6_interface, set_asbr, \
    set_hello_ival, route_summary_v2, set_dead_ival, bandwidth_block, ipv6_point_to_point, route_summary_v3
from templates.router import INTERFACE_BLOCK

"""
todo: cost and reference bandwidth modification is not yet implemented
"""

DEFAULT_HELLO_INTERVAL = 10
DEFAULT_DEAD_INTERVAL = 40


class OSPFv2Network(Provisionable):
    def __init__(self, net_addr: IPv4Address, area=0):
        self.net_addr = net_addr
        self.area = area

    def provision(self):
        return network.format(
            net_addr=self.net_addr.get_ip_addr(),
            wildcard_mask=self.net_addr.get_wildcard_mask(),
            area_id=self.area
        )

    def get_network(self):
        return self.net_addr


class OSPFInterface(Provisionable):
    def __init__(self, intf: str,
                 hello_interval=DEFAULT_HELLO_INTERVAL,
                 dead_interval=DEFAULT_DEAD_INTERVAL,
                 bandwidth=None):
        self.intf = intf
        self.hello_interval=hello_interval
        self.dead_interval=dead_interval
        self.bandwidth = bandwidth

    def provision(self):
        body = (set_hello_ival.format(seconds=self.hello_interval) if self.hello_interval != DEFAULT_HELLO_INTERVAL else "") \
            + (set_dead_ival.format(seconds=self.dead_interval) if self.dead_interval != DEFAULT_DEAD_INTERVAL else "") \
            + (bandwidth_block.format(speed=self.bandwidth) if self.bandwidth is not None else "")
        return INTERFACE_BLOCK.format(
            intf=self.intf,
            body=body
        )


class OSPFv3Interface(OSPFInterface):
    def __init__(self, intf_name,
                 area=0,
                 hello_interval=DEFAULT_HELLO_INTERVAL,
                 dead_interval=DEFAULT_DEAD_INTERVAL,
                 bandwidth=None,
                 ipv6_ptp=False):
        super().__init__(intf_name, hello_interval, dead_interval, bandwidth)
        self.area = area
        self.process_id = None
        self.ipv6_ptp = ipv6_ptp

    def set_process_id(self, process_id) -> OSPFv3Interface:
        self.process_id = process_id
        return self

    def provision(self):
        addl = (set_hello_ival.format(seconds=self.hello_interval) if self.hello_interval != DEFAULT_HELLO_INTERVAL else "") \
               + (set_dead_ival.format(seconds=self.dead_interval) if self.dead_interval != DEFAULT_DEAD_INTERVAL else "") \
               + (bandwidth_block.format(speed=self.bandwidth) if self.bandwidth is not None else "") \
               + (ipv6_point_to_point if self.ipv6_ptp else "")
        return INTERFACE_BLOCK.format(
            intf=self.intf,
            body=ipv6_interface.format(process_id=self.process_id,
                                       area_id=self.area) + addl
        )


class OSPFv2RouteSummary(Provisionable):
    def __init__(self, area: int, summary_addr: IPv4Address):
        self.area = area
        self.summary_addr = summary_addr

    def provision(self):
        return route_summary_v2.format(area=self.area,
                                       addr=self.summary_addr.get_ip_addr(),
                                       net_mask=self.summary_addr.get_mask())


class OSPFv3RouteSummary(Provisionable):
    def __init__(self, area: int, summary_addr: IPv6Address):
        self.area = area
        self.summary_addr = summary_addr

    def provision(self):
        return route_summary_v3.format(area=self.area,
                                       addr_mask=self.summary_addr.get_cidr())



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
                 summaries: List[OSPFv2RouteSummary]=None,
                 interfaces: List[OSPFInterface]=None,
                 asbr=False):
        super().__init__(passive_interfaces, router_id, process_id, asbr)
        self.networks = networks if networks is not None else []
        self.interfaces = interfaces if interfaces is not None else []
        self.summaries = summaries if summaries is not None else []

    def provision(self):
        return ospf_setup.format(version_init=v2_init.format(process_id=self.process_id),
                                 router_id=self.router_id,
                                 networks=provision_group(self.networks),
                                 passive_interfaces=reduce(lambda a, x: a + x,
                                                           map(lambda p: passive_interface.format(intf=p),
                                                               self.passive_interfaces), ""),
                                 summaries=provision_group(self.summaries),
                                 asbr=set_asbr if self.asbr else ""
                                 ) + provision_group(self.interfaces)


class OSPFv3(OSPF):
    def __init__(self,
                 interfaces: List[OSPFv3Interface],
                 passive_interfaces: List[str],
                 router_id,
                 process_id,
                 summaries: List[OSPFv3RouteSummary]=None,
                 asbr=False):
        super().__init__(passive_interfaces, router_id, process_id, asbr)
        self.interfaces = list(map(lambda i: i.set_process_id(process_id), interfaces))
        self.summaries = summaries if summaries is not None else []

    def provision(self):
        return ospf_setup.format(
                          version_init=v3_init.format(process_id=self.process_id),
                          router_id=self.router_id,
                          networks="",
                          passive_interfaces=reduce(lambda a, x: a + x,
                                                    map(lambda p: passive_interface.format(intf=p),
                                                        self.passive_interfaces), ""),
                          summaries=provision_group(self.summaries),
                          asbr=set_asbr if self.asbr else ""
                          ) + provision_group(self.interfaces)
