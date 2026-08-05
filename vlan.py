from templates import *
from ip import IPAddress

class Vlan:
    """
    todo: a VLAN is a concept that transcends routers and switches, shouldn't provision, should just provide data
    """
    def __init__(self, name: str, number: int, ipv4: IPAddress=None, router_port=None, ipv6: IPAddress=None, dhcp: bool=False):
        self.name = name
        self.number = number
        self.ipv4_gateway = ipv4
        self.ipv6_gateway = ipv6
        self.router_port = router_port
        self.dhcp_enabled = dhcp

    def provision_ipv6(self) -> str:
        return CONFIG_IPV6_BLOCK.format(port=self.router_port, vlan=self.number, ipv6=self.ipv6_gateway) if self.ipv6_gateway is not None else ""

    def provision_ipv6_link_local(self) -> str:
        return CONFIG_IPV6_LINK_LOCAL_VLAN.format(port=self.router_port, vlan=self.number)

    def get_number(self) -> int:
        return self.number

    def get_name(self) -> str:
        return self.name

    def get_ipv4_gateway(self):
        return self.ipv4_gateway

    def get_dhcp_enabled(self):
        return self.dhcp_enabled

class NativeVlan:
    def __init__(self, number):
        self.number = number

    def provision_ipv6(self) -> str:
        return ""

    def provision_ipv6_link_local(self) -> str:
        return ""

    def provision_switch_trunk(self) -> str:
        return CONFIG_TRUNK_NATIVE.format(number=self.number)

    def get_number(self) -> int:
        return self.number

    def get_name(self) -> str:
        return "Native"
