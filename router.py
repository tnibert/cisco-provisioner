from functools import reduce
from templates import *
from device import Device
from vlan import Vlan, NativeVlan
from routes import StaticRoute
from ip import IPAddress
from typing import List, Union

class Port:
    def __init__(self, intf, ipv4: IPAddress, ipv6: IPAddress, link_local: bool=False, dce: bool=False):
        self.intf = intf
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.link_local = link_local
        self.dce = dce

    def provision(self):
        return CONFIG_ROUTER_PORT.format(intf=self.intf,
                                         ipv4=self.ipv4.get_ip_addr(),
                                         subnet_mask=self.ipv4.get_mask(),
                                         ipv6=self.ipv6,
                                         additional= CONFIG_IPV6_PORT.format(ipv6=self.ipv6.get_cidr()) if self.ipv6 is not None else "" \
                                                     + CONFIG_IPV6_LINK_LOCAL.format(addr="FE80::1") if self.link_local else "" \
                                                     + DCE if self.dce else "")


class RouterOnAStickPort:
    def __init__(self, intf: str, vlans: List[Union[Vlan|NativeVlan]]):
        self.intf = intf
        self.vlans = vlans

    def provision(self):
        return reduce(lambda a, x: a + x,
                      map(lambda v: v.provision_router_on_a_stick(),
                      self.vlans)) \
            + CONFIG_ROUTER_ON_A_STICK_CLOSE.format(port=self.intf)


class IPv4LoopbackPort:
    def __init__(self, ip: IPAddress, number: int):
        self.ip = ip
        self.number = number

    def provision(self):
        return CONFIG_LOOPBACK_IPV4.format(number=self.number, addr=self.ip.get_ip_addr(), mask=self.ip.get_mask())

class Router(Device):
    def __init__(self, hostname: str, ports: List[Union[Port|RouterOnAStickPort|IPv4LoopbackPort]]=None, routes: List[StaticRoute]=None, vlans: List[Vlan]=None):
        super().__init__(hostname, 4)
        self.ports = ports if ports is not None else []
        self.routes = routes if routes is not None else []

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

    def provision(self) -> str:
        return self.provision_basic() + self.provision_ports() + self.provision_routes()
