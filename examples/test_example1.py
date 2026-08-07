import unittest

from examples.example1 import devices
from utils import strip_blank_lines

class TestProvisionRouter(unittest.TestCase):
    def test_hq(self):
        expected = """hostname HQ
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
ip dhcp excluded-address 192.168.100.1
ip dhcp excluded-address 192.168.100.2
ip dhcp excluded-address 192.168.100.3
ip dhcp excluded-address 192.168.100.4
ip dhcp excluded-address 192.168.100.5
ip dhcp excluded-address 192.168.10.1
ip dhcp excluded-address 192.168.10.2
ip dhcp excluded-address 192.168.10.3
ip dhcp excluded-address 192.168.10.4
ip dhcp excluded-address 192.168.10.5
ip dhcp excluded-address 192.168.20.1
ip dhcp excluded-address 192.168.20.2
ip dhcp excluded-address 192.168.20.3
ip dhcp excluded-address 192.168.20.4
ip dhcp excluded-address 192.168.20.5
ip dhcp pool LAN1
network 192.168.100.0 255.255.255.0
default-router 192.168.100.1
domain-name cisco.com
 
ip dhcp pool LAN10
network 192.168.10.0 255.255.255.0
default-router 192.168.10.1
domain-name cisco.com
 
ip dhcp pool LAN20
network 192.168.20.0 255.255.255.0
default-router 192.168.20.1
domain-name cisco.com
 
interface g0/0
ip address 192.168.100.1 255.255.255.0
no shut
exit
interface s0/0/0
ip address 172.16.30.1 255.255.255.252
clock rate 128000
no shut
exit
interface loopback 0
ip address 209.165.200.1 255.255.255.0
exit
ip route 192.168.10.0 255.255.255.0 172.16.30.2 
ip route 192.168.20.0 255.255.255.0 172.16.30.2 
ip route 192.168.99.0 255.255.255.0 172.16.30.2 
"""
        result = strip_blank_lines(devices["HQ"].provision())
        self.assertEqual(result, strip_blank_lines(expected))

    def test_branch(self):
        expected = """hostname BRANCH
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
int g0/0.10
encapsulation dot1q 10
ip address 192.168.10.1 255.255.255.0
ip helper-address 172.16.30.1
int g0/0.20
encapsulation dot1q 20
ip address 192.168.20.1 255.255.255.0
ip helper-address 172.16.30.1
int g0/0.99
encapsulation dot1q 99
ip address 192.168.99.1 255.255.255.0
int g0/0.1000
encapsulation dot1q 1000 native
no shut
interface s0/0/0
ip address 172.16.30.2 255.255.255.252
no shut
exit
ip route 0.0.0.0 0.0.0.0 s0/0/0 172.16.30.1 
"""
        result = strip_blank_lines(devices["BRANCH"].provision())
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
vlan 10
name Sales
vlan 20
name IT
vlan 99
name Management
vlan 555
name Parking_Lot
vlan 1000
name Native
! SVI interface
int vlan 99
ip address 192.168.99.11 255.255.255.0
no shut
exit
ip default-gateway 192.168.99.1
! setup ssh - router vty 0 4, switch vty 0 15
ip domain-name cisco.com
crypto key generate rsa general-keys modulus 1024
username admin secret cisco
line vty 0 15
transport input ssh
login local
exit
ip ssh version 2
int range f0/1
switchport mode trunk
switchport trunk allow vlan 10,20,99,1000
switchport trunk native vlan 1000
! secure trunk ports
switchport nonegotiate
exit
int range f0/6
switchport mode access
switchport access vlan 10
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
int range f0/18
switchport mode access
switchport access vlan 20
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
int range f0/2-5,f0/7-17,f0/19-24,g0/1-2
switchport mode access
switchport access vlan 555
shut
exit
"""
        result = strip_blank_lines(devices["S1"].provision())
        self.assertEqual(result, strip_blank_lines(expected))


if __name__ == "__main__":
    unittest.main()
