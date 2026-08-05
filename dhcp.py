from typing import List
from functools import reduce

from ip import IPAddress
from templates import DHCP_V4_EXCLUDE, DHCP_V4_POOL_CREATE, DHCP_V4_DNS, DHCP_V4_DOMAIN_NAME, DHCP_V4_RELAY


class DHCPPool:
    def __init__(self, pool_name: str, net_addr: IPAddress, gw: IPAddress, dns_addr: IPAddress=None, domain_name: str=None):
        self.pool_name = pool_name
        self.net_addr = net_addr
        self.gw = gw
        self.dns_addr = dns_addr
        self.domain_name = domain_name

    def provision(self) -> str:
        additional = DHCP_V4_DNS.format(addr=self.dns_addr) if self.dns_addr is not None else "" \
                    + DHCP_V4_DOMAIN_NAME.format(domain=self.domain_name) if self.domain_name is not None else ""
        return DHCP_V4_POOL_CREATE.format(pool_name=self.pool_name,
                                          net_addr=self.net_addr.get_ip_addr(),
                                          mask=self.net_addr.get_mask(),
                                          gw=self.gw.get_ip_addr(),
                                          additional=additional)

class DHCPServer:
    def __init__(self, excluded_addrs: List[IPAddress], pools: List[DHCPPool]):
        self.excluded_addrs = excluded_addrs
        self.pools = pools

    def provision_excluded_addrs(self):
        return reduce(lambda a,x: a+x,
                      map(lambda a: DHCP_V4_EXCLUDE.format(addr=a.get_ip_addr()), self.excluded_addrs))

    def provision(self) -> str:
        return self.provision_excluded_addrs() \
                + reduce(lambda a,x: a+x,
                         map(lambda p: p.provision(), self.pools))

class DHCPRelay:
    def __init__(self, helper_addr: IPAddress):
        self.helper_addr = helper_addr

    def provision(self) -> str:
        return DHCP_V4_RELAY.format(addr=self.helper_addr.get_ip_addr())
