from cidr import cidr_prefix_to_netmask


class IPAddress:
    def __init__(self, ip: str, mask_bits: int):
        self.ip_addr = ip
        self.mask = mask_bits

    def get_ip_addr(self) -> str:
        return self.ip_addr

    def get_mask(self) -> str:
        return cidr_prefix_to_netmask(self.mask)

    def get_mask_len(self) -> int:
        return self.mask

    def get_cidr(self) -> str:
        return "{}/{}".format(self.ip_addr, self.mask)
