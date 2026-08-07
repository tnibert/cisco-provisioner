from typing import List
from functools import reduce

from ip import IPAddress
from templates.dhcp import DHCP_V4_EXCLUDE, DHCP_V4_POOL_CREATE, DHCP_DNS, DHCP_DOMAIN_NAME, DHCP_V4_RELAY, \
    DHCP_V6_POOL_CREATE, DHCP_V6_STATELESS_FLAGS, DHCP_V6_STATEFUL_FLAGS, DHCP_V6_STATEFUL_POOL_PREFIX
from exceptions import Unimplemented


# enum for dhcp v6 state
DHCPV6_SLAAC = 0
DHCPV6_STATELESS = 1
DHCPV6_STATEFUL = 2

DHCPV6_MODE_TO_FLAGS = {
    DHCPV6_STATELESS: DHCP_V6_STATELESS_FLAGS,
    DHCPV6_STATEFUL: DHCP_V6_STATEFUL_FLAGS
}

class DHCPPool:
    def __init__(self, pool_name: str, dns_addr: IPAddress=None, domain_name: str=None):
        self.pool_name = pool_name
        self.dns_addr = dns_addr
        self.domain_name = domain_name

    def provision_dns(self) -> str:
        return DHCP_DNS.format(addr=self.dns_addr.get_ip_addr()) if self.dns_addr is not None else ""

    def provision_domain(self) -> str:
        return DHCP_DOMAIN_NAME.format(domain=self.domain_name) if self.domain_name is not None else ""

    def provision(self):
        raise Unimplemented("use v4 or v6 dhcp")


class DHCPv4Pool(DHCPPool):
    def __init__(self, pool_name: str, net_addr: IPAddress, gw: IPAddress, dns_addr: IPAddress=None, domain_name: str=None):
        super().__init__(pool_name, dns_addr, domain_name)
        self.net_addr = net_addr
        self.gw = gw

    def provision(self) -> str:
        return DHCP_V4_POOL_CREATE.format(pool_name=self.pool_name,
                                          net_addr=self.net_addr.get_ip_addr(),
                                          mask=self.net_addr.get_mask(),
                                          gw=self.gw.get_ip_addr(),
                                          additional=self.provision_dns() + self.provision_domain())


class DHCPv6Pool(DHCPPool):
    def __init__(self, pool_name: str, dns_addr: IPAddress=None, domain_name: str=None, address_prefix: IPAddress=None):
        super().__init__(pool_name, dns_addr, domain_name)
        self.address_prefix = address_prefix

    def provision_address_prefix(self):
        return DHCP_V6_STATEFUL_POOL_PREFIX.format(addr=self.address_prefix.get_cidr()) if self.address_prefix is not None else ""

    def provision(self) -> str:
        return DHCP_V6_POOL_CREATE.format(pool_name=self.pool_name,
                                          additional=self.provision_address_prefix() + self.provision_dns() + self.provision_domain())


class DHCPServer:
    def __init__(self, pools: List[DHCPPool]):
        self.pools = pools


class DHCPv4Server(DHCPServer):
    def __init__(self, excluded_addrs: List[IPAddress], pools: List[DHCPv4Pool]):
        super().__init__(pools)
        self.excluded_addrs = excluded_addrs

    def provision_excluded_addrs(self):
        return reduce(lambda a,x: a+x,
                      map(lambda a: DHCP_V4_EXCLUDE.format(addr=a.get_ip_addr()), self.excluded_addrs))

    def provision(self) -> str:
        return self.provision_excluded_addrs() \
                + reduce(lambda a,x: a+x,
                         map(lambda p: p.provision(), self.pools))


class DHCPv6Server(DHCPServer):
    def __init__(self, pools: List[DHCPv6Pool]):
        super().__init__(pools)

    def provision(self) -> str:
        return reduce(lambda a,x: a+x, map(lambda p: p.provision(), self.pools))


class DHCPRelay:
    def __init__(self, helper_addr: IPAddress):
        self.helper_addr = helper_addr

    def provision(self) -> str:
        return DHCP_V4_RELAY.format(addr=self.helper_addr.get_ip_addr())
