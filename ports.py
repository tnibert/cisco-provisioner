from templates import *

class Ports:
    """
    Group of physical network interface, not TCP/UDP port
    """
    def __init__(self, ports):
        self.ports = ports

    def provision_switch_ports(self) -> str:
        return "!UNIMPLEMENTED\n"

class UnusedPorts(Ports):
    def __init__(self, ports):
        super().__init__(ports)

    def provision_switch_ports(self) -> str:
        return CONFIG_UNUSED_PORTS.format(ports=self.ports)

class TrunkPorts(Ports):
    def __init__(self, ports):
        super().__init__(ports)

    def provision_switch_ports(self) -> str:
        return CONFIG_TRUNK_PORTS.format(ports=self.ports)

class AccessPorts(Ports):
    def __init__(self, ports, access_vlan):
        super().__init__(ports)
        self.access_vlan = access_vlan

    def provision_switch_ports(self) -> str:
        return CONFIG_ACCESS_PORTS.format(ports=self.ports, access_vlan=self.access_vlan)

class EtherChannelPorts(Ports):
    def __init__(self, ports, chan_num):
        super().__init__(ports)
        self.chan_num = chan_num

    def provision_switch_ports(self) -> str:
        return CONFIG_ETHERCHANNEL_PORTS.format(ports=self.ports, chan_num=self.chan_num)
