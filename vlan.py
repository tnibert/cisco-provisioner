from templates import *
from cidr import cidr_prefix_to_netmask

class Vlan:
    def __init__(self, number, gw, mask_prefix, router_port, ipv6=None):
        self.number = number
        self.gateway = gw
        self.ipv6_gateway = ipv6
        self.mask = cidr_prefix_to_netmask(mask_prefix)
        self.router_port = router_port

    def provision_router_on_a_stick(self) -> str:
        return CONFIG_ROUTER_ON_A_STICK_BLOCK.format(vlan=self.number, gw=self.gateway, mask=self.mask, port=self.router_port, ipv6=self.ipv6_gateway)

    def provision_ipv6(self) -> str:
        return CONFIG_IPV6_BLOCK.format(port=self.router_port, vlan=self.number, ipv6=self.ipv6_gateway) if self.ipv6_gateway is not None else ""

    def provision_ipv6_link_local(self) -> str:
        return CONFIG_IPV6_LINK_LOCAL_VLAN.format(port=self.router_port, vlan=self.number)

class NativeVlan:
    def __init__(self, number, router_port):
        self.number = number
        self.router_port = router_port

    def provision_router_on_a_stick(self) -> str:
        return CONFIG_NATIVE_ROUTER_ON_A_STICK_BLOCK.format(vlan=self.number, port=self.router_port)

    def provision_ipv6(self) -> str:
        return ""

    def provision_ipv6_link_local(self) -> str:
        return ""
