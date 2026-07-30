from functools import reduce
from templates import *
from device import Device
from vlan import Vlan
from typing import List

class InsufficientInfo(Exception):
    pass

class StaticRoute:
    def __init__(self, net_addr, next_hop=None, interface=None, administrative_distance=None):
        self.net_addr = net_addr
        if next_hop is None and interface is None:
            raise InsufficientInfo("need one of next_hop and interface specified")
        self.next_hop = next_hop
        self.interface = interface
        self.ad = administrative_distance

class StaticIPv4Route(StaticRoute):
    def __init__(self, net_addr, subnet_mask, next_hop=None, interface=None, administrative_distance=None):
        super().__init__(net_addr, next_hop, interface, administrative_distance)
        self.subnet_mask = subnet_mask

    def provision(self):
        if self.next_hop is not None and self.interface is not None:
            return STATIC_ROUTES["IPV4_FULLY_SPECIFIED"].format(net_addr=self.net_addr,
                                                                subnet_mask=self.subnet_mask,
                                                                intf=self.interface,
                                                                next_hop=self.next_hop,
                                                                ad=self.ad if self.ad is not None else "")
        elif self.next_hop is not None:
            return STATIC_ROUTES["IPV4_NEXT_HOP"].format(net_addr=self.net_addr,
                                                         subnet_mask=self.subnet_mask,
                                                         next_hop=self.next_hop,
                                                         ad=self.ad if self.ad is not None else "")
        elif self.interface is not None:
            return STATIC_ROUTES["IPV4_DIRECTLY_CONNECTED"].format(net_addr=self.net_addr,
                                                                   subnet_mask=self.subnet_mask,
                                                                   intf=self.interface,
                                                                   ad=self.ad if self.ad is not None else "")
        raise InsufficientInfo("can't provision ipv4 route")

class StaticIPv6Route(StaticRoute):
    def __init__(self, net_addr, next_hop=None, interface=None, administrative_distance=None):
        super().__init__(net_addr, next_hop, interface, administrative_distance)

    def provision(self):
        if self.next_hop is not None and self.interface is not None:
            return STATIC_ROUTES["IPV6_FULLY_SPECIFIED"].format(net_addr=self.net_addr,
                                                                intf=self.interface,
                                                                next_hop=self.next_hop,
                                                                ad=self.ad if self.ad is not None else "")
        elif self.next_hop is not None:
            return STATIC_ROUTES["IPV6_NEXT_HOP"].format(net_addr=self.net_addr,
                                                         next_hop=self.next_hop,
                                                         ad=self.ad if self.ad is not None else "")
        elif self.interface is not None:
            return STATIC_ROUTES["IPV6_DIRECTLY_CONNECTED"].format(net_addr=self.net_addr,
                                                                   intf=self.interface,
                                                                   ad=self.ad if self.ad is not None else "")
        raise InsufficientInfo("can't provision ipv6 route")

class Port:
    def __init__(self, intf, ipv4, subnet_mask, ipv6, link_local: bool=False, dce: bool=False):
        self.intf = intf
        self.ipv4 = ipv4
        self.subnet_mask = subnet_mask
        self.ipv6 = ipv6
        self.link_local = link_local
        self.dce = dce

    def provision(self):
        return CONFIG_ROUTER_PORT.format(intf=self.intf, ipv4=self.ipv4, subnet_mask=self.subnet_mask, ipv6=self.ipv6,
                                         additional=CONFIG_IPV6_LINK_LOCAL.format(addr="FE80::1") if self.link_local else "" + DCE if self.dce else "")


class Router(Device):
    def __init__(self, hostname: str, ports: List[Port]=None, routes: List[StaticRoute]=None, vlans: List[Vlan]=None):
        super().__init__(hostname, 4)
        self.vlans = vlans if vlans is not None else []
        self.ports = ports if ports is not None else []
        self.routes = routes if routes is not None else []

    def provision_router_on_a_stick(self) -> str:
        provisioning = reduce(lambda a, x: a + x,
                          map(lambda v: v.provision_router_on_a_stick(),
                              self.vlans)) \
                        + CONFIG_ROUTER_ON_A_STICK_CLOSE.format(port="G0/0") \
                        + CONFIG_ROUTER_ON_A_STICK_CLOSE.format(port="G0/1")

        return "configure terminal\n" + provisioning + "exit\nexit\n"

    def provision_ipv6(self) -> str:
        return reduce(lambda a, x: a + x,
                  map(lambda v: v.provision_ipv6(),
                      self.vlans), "")

    def provision_ipv6_link_local(self) -> str:
        """
        This would not be desired for management or parking lot vlans
        """
        return reduce(lambda a, x: a + x,
                  map(lambda v: v.provision_ipv6_link_local(),
                      self.vlans), "")

    def provision_ports(self):
        return reduce(lambda a, x: a + x,
                      map(lambda v: v.provision(),
                          self.ports), "")

    def provision_routes(self):
        return reduce(lambda a, x: a + x,
                      map(lambda v: v.provision(),
                          self.routes), "")

    def all_provisioning(self) -> str:
        return self.provision_basic() #+ self.provision_router_on_a_stick() + self.provision_ipv6()
