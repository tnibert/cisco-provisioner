import sys

from router import Router, Port, StaticIPv4Route, StaticIPv6Route
from switch import Switch
from ports import *
from cidr import CIDR

HQ_S001_IPV4 = "192.168.0.253"
HQ_S001_IPV6 = "2001:DB8:ACAD:2::1"
HQ_G01_IPV4 = "10.1.1.2"
HQ_G01_IPV6 = "2001:DB8:ACAD:20::2"
HQ_G02_IPV4 = "10.1.1.6"
HQ_G02_IPV6 = "2001:DB8:ACAD:21::2"
BRANCH_G00_IPV4 = "192.168.1.1"
BRANCH_G00_IPV6 = "2001:DB8:ACAD:1::1"
BRANCH_S000_IPV4 = "192.168.0.254"
BRANCH_S000_IPV6 = "2001:DB8:ACAD:2::2"
ISP_G01_IPV4 = "10.1.1.1"
ISP_GO1_IPV6 = "2001:DB8:ACAD:20::1"
ISP_G02_IPV4 = "10.1.1.5"
ISP_GO2_IPV6 = "2001:DB8:ACAD:21::1"

format_octet_binary = lambda n: '{0:08b}'.format(n)

devices = {
    "S1": Switch("S1", None, None,
                 [
                     UnusedPorts("f0/1-4,f0/7-24,g0/1-2"),
                 ]),
    "S3": Switch("S3", None, None,
                 [
                     UnusedPorts("f0/1-4,f0/6-17,f0/19-24,g0/1-2"),
                 ]),
    "ISP": Router("ISP",
                  [
                      Port("g0/0", "172.16.3.1", CIDR[24], "2001:DB8:ACAD:30::1/64", link_local=True),
                      Port("g0/1", ISP_G01_IPV4, CIDR[30], ISP_GO1_IPV6),
                      Port("g0/2", ISP_G02_IPV4, CIDR[30], ISP_GO2_IPV6)
                   ],
                  [
                      StaticIPv4Route("192.168.0.0", "255.255.254.0", HQ_G01_IPV4, "g0/1"),
                      StaticIPv6Route("2001:DB8:ACAD::/59", HQ_G01_IPV6, "g0/2"),
                      StaticIPv4Route("192.168.0.0", "255.255.254.0", HQ_G02_IPV4, administrative_distance=80),
                      StaticIPv6Route("2001:DB8:ACAD::/59", HQ_G02_IPV6, administrative_distance=80),
                  ]),
    "BRANCH": Router("BRANCH",
                     [
                         Port("g0/0", BRANCH_G00_IPV4, CIDR[24], BRANCH_G00_IPV6, link_local=True),
                         Port("s0/0/0", "192.168.0.254", CIDR[30], "2001:DB8:ACAD:2::2/64", dce=True)
                     ],
                     [
                         StaticIPv4Route("0.0.0.0", "0.0.0.0", HQ_S001_IPV4, "s0/0/0"),
                         StaticIPv6Route("::/0", HQ_S001_IPV6, "s0/0/0")
                     ]),
    "HQ": Router("HQ",
                 [
                     Port("g0/0", "192.168.0.1", CIDR[25], "2001:DB8:ACAD::1/64", link_local=True),
                     Port("g0/1", HQ_G01_IPV4, CIDR[30], HQ_G01_IPV6),
                     Port("g0/2", HQ_G02_IPV4, CIDR[30], HQ_G02_IPV6),
                     Port("s0/0/1", HQ_S001_IPV4, CIDR[30], HQ_S001_IPV6)
                 ],
                 [
                     StaticIPv4Route("192.168.1.0", CIDR[24], BRANCH_S000_IPV4, "s0/0/1"),
                     StaticIPv6Route("2001:DB8:ACAD:1::/64", BRANCH_S000_IPV6, "s0/0/1"),
                     StaticIPv4Route("0.0.0.0", "0.0.0.0", ISP_G01_IPV4, "g0/1"),
                     StaticIPv6Route("::/0", ISP_GO1_IPV6, "g0/1"),
                     StaticIPv4Route("0.0.0.0", "0.0.0.0", ISP_G02_IPV4, administrative_distance=80),
                     StaticIPv6Route("::/0", ISP_GO2_IPV6, administrative_distance=80)
                 ])
}

if __name__=='__main__':
    """
    generate provisioning commands
    """
    if len(sys.argv) > 1:
        print(devices[sys.argv[1]].all_provisioning())
        #print(s.provision_basic_switch())
        #print(s.provision_ssh())
        #for p in s.port_configs:
        #    print(p.provision_switch_ports())
    else:
        # all
        for k,v in devices.items():
            try:
                config = v.provision_routes()
            except AttributeError:
                continue
            print(f"-----{k}-----")
            print(config)
