from functools import reduce

from acl import ACL
from dhcp import DHCPServer, DHCPRelay, DHCPV6_SLAAC, DHCPV6_MODE_TO_FLAGS
from nat import NAT
from provisionable import provision_group, Provisionable
from templates.dhcp import DHCP_V6_SERVER_CREATE
from templates.router import (CONFIG_IPV4_PORT, CONFIG_IPV6_PORT, CONFIG_IPV6_LINK_LOCAL, DCE,
                              CONFIG_ROUTER_ON_A_STICK_BLOCK, CONFIG_NATIVE_ROUTER_ON_A_STICK_BLOCK,
                              CONFIG_LOOPBACK_IPV4, INTERFACE_BLOCK, ENABLE_IPV6)
from templates.common import PORT_NO_SHUT
from device import Device
from utils import strip_blank_lines, partition
from vlan import VlanUnion, NativeVlan
from routes import StaticRoute
from exceptions import Unimplemented
from ip import IPAddress
from typing import List, Union

class BasePort:
    def __init__(self, intf: str, dce: bool=False, dhcp_relay: DHCPRelay=None, dhcpv6_pool: str=None, dhcpv6_mode=DHCPV6_SLAAC):
        self.intf = intf
        self.dce = dce
        self.dhcp_relay = dhcp_relay
        self.dhcpv6_pool = dhcpv6_pool
        self.dhcpv6_mode = dhcpv6_mode

    def provision(self):
        raise Unimplemented("use a port implementation")

    def provision_dce(self) -> str:
        return DCE if self.dce else ""

    def provision_dhcp_relay(self) -> str:
        return self.dhcp_relay.provision() if self.dhcp_relay is not None else ""

    def provision_dhcp_v6(self) -> str:
        if self.dhcpv6_pool is not None and self.dhcpv6_mode != DHCPV6_SLAAC:
            return DHCP_V6_SERVER_CREATE.format(pool_name=self.dhcpv6_pool,
                                                flags=DHCPV6_MODE_TO_FLAGS[self.dhcpv6_mode])
        else:
            return ""


class OrdinaryPort(BasePort):
    def __init__(self,
                 intf,
                 ipv4: IPAddress,
                 ipv6: IPAddress=None,
                 link_local: IPAddress=None,
                 dce: bool=False,
                 dhcp_relay=None,
                 dhcpv6_pool: str=None,
                 dhcpv6_mode=DHCPV6_SLAAC):
        super().__init__(intf, dce, dhcp_relay, dhcpv6_pool, dhcpv6_mode)
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.link_local = link_local

    def provision_ipv4(self) -> str:
        return CONFIG_IPV4_PORT.format(ipv4=self.ipv4.get_ip_addr(), subnet_mask=self.ipv4.get_mask()) if self.ipv4 is not None else ""

    def provision_ipv6(self) -> str:
        return CONFIG_IPV6_PORT.format(ipv6=self.ipv6.get_cidr()) if self.ipv6 is not None else ""

    def provision_ipv6_link_local(self) -> str:
        return CONFIG_IPV6_LINK_LOCAL.format(addr=self.link_local.get_ip_addr()) if self.link_local is not None else ""

    def provision(self):
        return INTERFACE_BLOCK.format(intf=self.intf,
                                      body= self.provision_ipv4() \
                                           + self.provision_ipv6() \
                                           + self.provision_ipv6_link_local() \
                                           + self.provision_dce() \
                                           + self.provision_dhcp_relay() \
                                           + self.provision_dhcp_v6() \
                                           + PORT_NO_SHUT)


class RouterOnAStickPort(BasePort):
    def __init__(self, intf: str, vlans: List[VlanUnion], dhcp_relay=None):
        super().__init__(intf, False, dhcp_relay)
        self.vlans = vlans

    def provision(self):
        """
        Todo: bring this into alignment with design of OrdinaryPort::provision()
        """
        regular_vlans, native_vlans = partition(lambda v: not isinstance(v, NativeVlan), self.vlans)
        return reduce(lambda a, x: a + x,
                      map(lambda v: CONFIG_ROUTER_ON_A_STICK_BLOCK.format(
                          vlan=v.get_number(),
                          gw=v.get_ipv4_gateway().get_ip_addr(),
                          mask=v.get_ipv4_gateway().get_mask(),
                          port=self.intf,
                          additional=self.dhcp_relay.provision() if self.dhcp_relay is not None and v.get_dhcp_enabled() else ""),
                      regular_vlans)) \
            + reduce(lambda a,x: a+x,
                     map(lambda v: CONFIG_NATIVE_ROUTER_ON_A_STICK_BLOCK.format(vlan=v.get_number(), port=self.intf),
                         native_vlans)) \
            + INTERFACE_BLOCK.format(intf=self.intf, body=PORT_NO_SHUT)


class IPv4LoopbackPort:
    def __init__(self, ip: IPAddress, number: int):
        self.ip = ip
        self.number = number

    def provision(self):
        return CONFIG_LOOPBACK_IPV4.format(number=self.number, addr=self.ip.get_ip_addr(), mask=self.ip.get_mask())


PortUnion = Union[BasePort | IPv4LoopbackPort]

class Router(Device):
    def __init__(self, hostname: str,
                 ports: List[PortUnion]=None,
                 routes: List[StaticRoute]=None,
                 dhcp_servers: List[DHCPServer]=None,
                 dynamic_routing: List[Provisionable]=None,
                 acls: List[ACL]=None,
                 nat: NAT=None):
        super().__init__(hostname, 4)
        self.ports = ports if ports is not None else []
        self.routes = routes if routes is not None else []
        self.dhcp_servers = dhcp_servers if dhcp_servers is not None else []
        self.dynamic_routing = dynamic_routing if dynamic_routing is not None else []
        self.acls = acls if acls is not None else []
        self.nat = nat

    def provision_ports(self):
        return provision_group(self.ports)

    def provision_routes(self):
        return provision_group(self.routes)

    def provision_dhcp(self):
        return provision_group(self.dhcp_servers)

    def provision_dynamic_routing(self):
        return provision_group(self.dynamic_routing)

    def provision_acls(self):
        return provision_group(self.acls)

    def provision_nat(self):
        return self.nat.provision() if self.nat is not None else ""

    def provision(self) -> str:
        return strip_blank_lines(
            self.provision_basic() \
            + ENABLE_IPV6 \
            + self.provision_dhcp() \
            + self.provision_ports() \
            + self.provision_routes() \
            + self.provision_dynamic_routing() \
            + self.provision_acls() \
            + self.provision_nat()
        )
