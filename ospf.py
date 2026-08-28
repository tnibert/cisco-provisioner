from functools import reduce
from typing import List

from exceptions import InvalidOption
from ip import IPAddress
from provisionable import Provisionable
from templates.ospf import ospf_setup, network, passive_interface, v2_init, v3_init

V2 = "v2"
V3 = "v3"

init = {
    V2: v2_init,
    V3: v3_init
}

class OSPF(Provisionable):
    def __init__(self, networks: List[IPAddress], passive_interfaces: List[str], version, router_id, process_id):
        self.networks = networks if networks is not None else []
        self.passive_interfaces = passive_interfaces if passive_interfaces is not None else []

        if version not in (V2, V3):
            raise InvalidOption("need to specify a valid OSPF version")
        self.version = version
        self.router_id = router_id
        self.process_id = process_id

    def provision(self):
        return ospf_setup.format(version_init=init[self.version].format(process_id=self.process_id),
                                 router_id=self.router_id,
                                 networks=reduce(lambda a,x: a+x,
                                                map(lambda n: network.format(
                                                        net_addr=n.get_ip_addr(),
                                                        wildcard_mask=n.get_wildcard_mask(),
                                                        area_id=0
                                                    ),
                                                    self.networks), ""),
                                passive_interfaces=reduce(lambda a,x: a+x,
                                                          map(lambda p: passive_interface.format(intf=p),
                                                              self.passive_interfaces), ""),
                                )
