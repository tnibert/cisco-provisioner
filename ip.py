import socket
import struct

from exceptions import InvalidConfig

# just a shortcut
CIDR_CACHE = {
    24: "255.255.255.0",
    25: "255.255.255.128",
    30: "255.255.255.252"
}

DEFAULT_IPV6_MASK = 64

def cidr_prefix_to_netmask(net_bits):
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask

def cidr_prefix_to_wildcard_mask(net_bits):
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1<<32) - ((1 << 32) - (1 << host_bits)) - 1))
    return netmask


class IPAddress:
    def __init__(self, ip: str, mask_bits: int):
        self.ip_addr = ip
        self.mask = mask_bits

    def get_ip_addr(self) -> str:
        return self.ip_addr

    def get_mask_len(self) -> int:
        return self.mask

    def get_cidr(self) -> str:
        return "{}/{}".format(self.ip_addr, self.mask)


class IPv4Address(IPAddress):
    def get_mask(self) -> str:
        return cidr_prefix_to_netmask(self.mask)

    def get_wildcard_mask(self) -> str:
        return cidr_prefix_to_wildcard_mask(self.mask)


class IPv6Address(IPAddress):
    def __init__(self, ip: str, mask_bits: int=DEFAULT_IPV6_MASK):
        super().__init__(ip, mask_bits)


class IPv4Range:
    def __init__(self, start: IPv4Address, end: IPv4Address):
        if start.get_mask_len() != end.get_mask_len():
            raise InvalidConfig()
        self.start = start
        self.end = end

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_mask(self):
        return self.start.get_mask()
