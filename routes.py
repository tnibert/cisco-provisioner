from ip import IPAddress
from templates import STATIC_ROUTES
from exceptions import InsufficientInfo

class StaticRoute:
    def __init__(self, net_addr: IPAddress, next_hop: IPAddress=None, interface=None, administrative_distance=None):
        self.net_addr = net_addr
        if next_hop is None and interface is None:
            raise InsufficientInfo("need one of next_hop and interface specified")
        self.next_hop = next_hop
        self.interface = interface
        self.ad = administrative_distance

class StaticIPv4Route(StaticRoute):
    def __init__(self, net_addr: IPAddress, next_hop: IPAddress=None, interface=None, administrative_distance=None):
        super().__init__(net_addr, next_hop, interface, administrative_distance)

    def provision(self):
        if self.next_hop is not None and self.interface is not None:
            return STATIC_ROUTES["IPV4_FULLY_SPECIFIED"].format(net_addr=self.net_addr.get_ip_addr(),
                                                                subnet_mask=self.net_addr.get_mask(),
                                                                intf=self.interface,
                                                                next_hop=self.next_hop.get_ip_addr(),
                                                                ad=self.ad if self.ad is not None else "")
        elif self.next_hop is not None:
            return STATIC_ROUTES["IPV4_NEXT_HOP"].format(net_addr=self.net_addr.get_ip_addr(),
                                                         subnet_mask=self.net_addr.get_mask(),
                                                         next_hop=self.next_hop.get_ip_addr(),
                                                         ad=self.ad if self.ad is not None else "")
        elif self.interface is not None:
            return STATIC_ROUTES["IPV4_DIRECTLY_CONNECTED"].format(net_addr=self.net_addr.get_ip_addr(),
                                                                   subnet_mask=self.net_addr.get_mask(),
                                                                   intf=self.interface,
                                                                   ad=self.ad if self.ad is not None else "")
        raise InsufficientInfo("can't provision ipv4 route")

class StaticIPv6Route(StaticRoute):
    def __init__(self, net_addr: IPAddress, next_hop: IPAddress=None, interface=None, administrative_distance=None):
        super().__init__(net_addr, next_hop, interface, administrative_distance)

    def provision(self):
        if self.next_hop is not None and self.interface is not None:
            return STATIC_ROUTES["IPV6_FULLY_SPECIFIED"].format(net_addr=self.net_addr.get_cidr(),
                                                                intf=self.interface,
                                                                next_hop=self.next_hop.get_ip_addr(),
                                                                ad=self.ad if self.ad is not None else "")
        elif self.next_hop is not None:
            return STATIC_ROUTES["IPV6_NEXT_HOP"].format(net_addr=self.net_addr.get_cidr(),
                                                         next_hop=self.next_hop.get_ip_addr(),
                                                         ad=self.ad if self.ad is not None else "")
        elif self.interface is not None:
            return STATIC_ROUTES["IPV6_DIRECTLY_CONNECTED"].format(net_addr=self.net_addr.get_cidr(),
                                                                   intf=self.interface,
                                                                   ad=self.ad if self.ad is not None else "")
        raise InsufficientInfo("can't provision ipv6 route")