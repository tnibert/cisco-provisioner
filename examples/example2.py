from ip import IPAddress
from switch import Switch
from router import Router, OrdinaryPort
from ports import AccessPorts, UnusedPorts
from dhcp import DHCPv6Server, DHCPv6Pool, DHCPV6_STATELESS, DHCPV6_STATEFUL

DOMAIN = "cisco.com"

MASK_LEN = 64
r1_g00_ip = IPAddress("2001:db8:acad:2::1", MASK_LEN)
r1_g01_ip = IPAddress("2001:db8:acad:1::1", MASK_LEN)
dns_addr = IPAddress("2001:db8:acad::254", MASK_LEN)
dhcpv6_addr_prefix = IPAddress("2001:db8:acad:2:aaaa::", 80)

devices = {
    "S1": Switch("S1", None, None, None,
                 [
                     AccessPorts("f0/5-6"),
                     UnusedPorts("f0/1-4,f0/7-24,g0/1-2"),
                 ]),
    "S2": Switch("S2", None, None, None,
                 [
                     AccessPorts("f0/5,f0/18"),
                     UnusedPorts("f0/1-4,f0/6-17,f0/19-24,g0/1-2"),
                 ]),
    "R1": Router("R1",
                 [
                     OrdinaryPort("g0/0", None, r1_g00_ip, IPAddress("FE80::1", MASK_LEN), dhcpv6_pool="R1-STATEFUL", dhcpv6_mode=DHCPV6_STATEFUL),
                     OrdinaryPort("g0/1", None, r1_g01_ip, IPAddress("FE80::1", MASK_LEN), dhcpv6_pool="R1-STATELESS", dhcpv6_mode=DHCPV6_STATELESS)
                 ],
                 [

                 ],
                 [
                    DHCPv6Server([
                        DHCPv6Pool("R1-STATELESS", dns_addr, DOMAIN),
                        DHCPv6Pool("R1-STATEFUL", dns_addr, DOMAIN, dhcpv6_addr_prefix)
                    ])
                 ]),
}
