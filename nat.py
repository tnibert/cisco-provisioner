from functools import reduce
from typing import List

from acl import ACL
from ip import IPv4Range
from provisionable import Provisionable
from templates.nat import static_nat_setup, nat_inside, nat_outside, bind_acl_pool, bind_acl_pool_pat, \
    dynamic_nat_pool_setup
from templates.router import INTERFACE_BLOCK


class NAT(Provisionable): pass


class StaticNAT(NAT):
    def __init__(self, local_ip, global_ip, inside_intf, outside_intf):
        self.local_ip = local_ip
        self.global_ip = global_ip
        self.inside_intf = inside_intf
        self.outside_intf = outside_intf

    def provision(self):
        return static_nat_setup.format(local_ip=self.local_ip.get_ip_addr(), global_ip=self.global_ip.get_ip_addr()) \
                + INTERFACE_BLOCK.format(intf=self.inside_intf, body=nat_inside) \
                + INTERFACE_BLOCK.format(intf=self.outside_intf, body=nat_outside)


class NATAddressPool(Provisionable):
    def __init__(self, pool_name, acl: ACL, range: IPv4Range, overload: bool=False):
        self.pool_name = pool_name
        self.acl = acl
        self.range = range
        self.overload = overload

    def bind(self):
        bind_cmd = bind_acl_pool if not self.overload else bind_acl_pool_pat
        return bind_cmd.format(acl_identifier=self.acl.get_identifier(), pool_name=self.pool_name)

    def provision(self):
        return dynamic_nat_pool_setup.format(pool_name=self.pool_name,
                                             start_addr=self.range.get_start().get_ip_addr(),
                                             end_addr=self.range.get_end().get_ip_addr(),
                                             netmask=self.range.get_mask()) + self.bind()


class DynamicNAT(NAT):
    def __init__(self, addr_pool: NATAddressPool, inside_intfs: List, outside_intfs: List):
        self.pool = addr_pool
        self.inside_intfs = inside_intfs
        self.outside_intfs = outside_intfs

    def inside(self):
        return reduce(lambda a, x: a + x,
                      map(lambda i: INTERFACE_BLOCK.format(intf=i, body=nat_inside),
                          self.inside_intfs), "")

    def outside(self):
        return reduce(lambda a, x: a + x,
                      map(lambda i: INTERFACE_BLOCK.format(intf=i, body=nat_outside),
                          self.outside_intfs), "")

    def provision(self):
        return self.pool.provision() + self.inside() + self.outside()


class PAT(NAT):
    def __init__(self):
        pass

    def provision(self):
        pass
