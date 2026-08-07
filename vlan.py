from ip import IPAddress
from templates.switch import CONFIG_TRUNK_NATIVE
from typing import Union

class Vlan:
    def __init__(self, name: str, number: int, ipv4: IPAddress=None, router_port=None, ipv6: IPAddress=None, dhcp: bool=False):
        self.name = name
        self.number = number
        self.ipv4_gateway = ipv4
        self.ipv6_gateway = ipv6
        self.router_port = router_port
        self.dhcp_enabled = dhcp

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

    def provision_switch_trunk(self) -> str:
        """
        todo: move to Switch
        """
        return CONFIG_TRUNK_NATIVE.format(number=self.number)

    def get_number(self) -> int:
        return self.number

    def get_name(self) -> str:
        return "Native"


VlanUnion = Union[Vlan|NativeVlan]
