from functools import reduce
from templates import *

class Router:
    def __init__(self, vlans: List[Vlan]):
        self.vlans = vlans

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
                      self.vlans))

    def provision_ipv6_link_local(self) -> str:
        """
        This would not be desired for management or parking lot vlans
        """
        return reduce(lambda a, x: a + x,
                  map(lambda v: v.provision_ipv6_link_local(),
                      self.vlans))

    def all_provisioning(self) -> str:
        return self.provision_router_on_a_stick() + self.provision_ipv6()
