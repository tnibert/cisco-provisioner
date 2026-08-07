import unittest

from examples.example2 import devices
from utils import strip_blank_lines

class TestProvisionRouter(unittest.TestCase):
    def test_all(self):
        expected = """hostname R1
no ip domain-lookup
enable secret class
line console 0
password cisco
login
logging synchronous
exit
line vty 0 4
password cisco
login
logging synchronous
exit
service password-encryption
banner motd $ Authorized Access Only! $
ipv6 unicast-routing
ipv6 dhcp pool R1-STATELESS
dns-server 2001:db8:acad::254
domain-name cisco.com
exit
ipv6 dhcp pool R1-STATEFUL
address prefix 2001:db8:acad:2:aaaa::/80
dns-server 2001:db8:acad::254
domain-name cisco.com
exit
interface g0/0
ipv6 address 2001:db8:acad:2::1/64
ipv6 address FE80::1 link-local
ipv6 dhcp server R1-STATEFUL
ipv6 nd managed-config-flag
ipv6 nd prefix default no-autoconfig
no shut
exit
interface g0/1
ipv6 address 2001:db8:acad:1::1/64
ipv6 address FE80::1 link-local
ipv6 dhcp server R1-STATELESS
ipv6 nd other-config-flag
no shut
exit
"""
        result = strip_blank_lines(devices["R1"].provision())
        self.assertEqual(result, strip_blank_lines(expected))


class TestProvisionSwitch(unittest.TestCase):
    def test_s1(self):
        expected = """hostname S1
no ip domain-lookup
enable secret class
line console 0
password cisco
login
logging synchronous
exit
line vty 0 15
password cisco
login
logging synchronous
exit
service password-encryption
banner motd $ Authorized Access Only! $
int range f0/5-6
switchport mode access
! portfast and BPDU
spanning-tree portfast
spanning-tree bpduguard enable
! secure access ports
switchport port-security
switchport port-security max 1
switchport port-security mac-address sticky
switchport port-security violation shutdown
no shut
exit
! disable unused ports
int range f0/1-4,f0/7-24,g0/1-2
switchport mode access
switchport access vlan 555
shut
exit
"""
        result = strip_blank_lines(devices["S1"].provision())
        self.assertEqual(result, strip_blank_lines(expected))

    def test_s2(self):
        expected = """hostname S2
no ip domain-lookup
enable secret class
line console 0
password cisco
login
logging synchronous
exit
line vty 0 15
password cisco
login
logging synchronous
exit
service password-encryption
banner motd $ Authorized Access Only! $
int range f0/5,f0/18
switchport mode access
! portfast and BPDU
spanning-tree portfast
spanning-tree bpduguard enable
! secure access ports
switchport port-security
switchport port-security max 1
switchport port-security mac-address sticky
switchport port-security violation shutdown
no shut
exit
! disable unused ports
int range f0/1-4,f0/6-17,f0/19-24,g0/1-2
switchport mode access
switchport access vlan 555
shut
exit
"""
        result = strip_blank_lines(devices["S2"].provision())
        self.assertEqual(result, strip_blank_lines(expected))


if __name__ == "__main__":
    unittest.main()
