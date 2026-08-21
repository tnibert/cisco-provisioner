from functools import reduce
from typing import List

from ip import IPAddress
from templates.rip import rip_setup, network, passive_interface, default_route_propagate


class RIP:
    def __init__(self, networks: List[IPAddress], passive_interfaces: List[str], default_rt_propagate: bool=False):
        self.networks = networks if networks is not None else []
        self.passive_interfaces = passive_interfaces if passive_interfaces is not None else []
        self.default_route_propagate = default_rt_propagate

    def provision(self):
        return rip_setup.format(networks=reduce(lambda a,x: a+x,
                                                map(lambda n: network.format(net_addr=n.get_ip_addr()),
                                                    self.networks), ""),
                                passive_interfaces=reduce(lambda a,x: a+x,
                                                          map(lambda p: passive_interface.format(intf=p),
                                                              self.passive_interfaces), ""),
                                default_propagate=default_route_propagate if self.default_route_propagate else ""
                                )
