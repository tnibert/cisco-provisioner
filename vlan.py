from templates import *
from ip import IPAddress

class Vlan:
    """
    todo: a VLAN is a concept that transcends routers and switches, shouldn't provision, should just provide data
    """
    def __init__(self, name: str, number: int, ipv4: IPAddress=None, router_port=None, ipv6: IPAddress=None):
        self.name = name
        self.number = number
        self.ipv4_gateway = ipv4
        self.ipv6_gateway = ipv6
        self.router_port = router_port

    def provision_router_on_a_stick(self) -> str:
        if None in (self.number, self.router_port, self.ipv4_gateway):
            return ""
        else:
            return CONFIG_ROUTER_ON_A_STICK_BLOCK.format(vlan=self.number,
                                                         gw=self.ipv4_gateway.get_ip_addr(),
                                                         mask=self.ipv4_gateway.get_mask(),
                                                         port=self.router_port)

    def provision_ipv6(self) -> str:
        return CONFIG_IPV6_BLOCK.format(port=self.router_port, vlan=self.number, ipv6=self.ipv6_gateway) if self.ipv6_gateway is not None else ""

    def provision_ipv6_link_local(self) -> str:
        return CONFIG_IPV6_LINK_LOCAL_VLAN.format(port=self.router_port, vlan=self.number)

    def provision_switch_vlan(self) -> str:
        return CONFIG_SWITCH_VLAN.format(number=self.number, name=self.name)

    def get_number(self) -> int:
        return self.number

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

    def provision_switch_trunk(self) -> str:
        return CONFIG_TRUNK_NATIVE.format(number=self.number)

    def provision_switch_vlan(self) -> str:
        return CONFIG_SWITCH_VLAN.format(number=self.number, name="Native")

    def get_number(self) -> int:
        return self.number
