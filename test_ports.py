from unittest import TestCase

from ports import EtherChannelPorts
from vlan import Vlan, NativeVlan


class TestEtherChannelPorts(TestCase):
    def test_provision(self):
        port = EtherChannelPorts("f0/2-3", 1, [
            Vlan("test1", 10),
            Vlan("test2", 20),
            NativeVlan(1000)
        ])
        result = port.provision()
        assert result == """
! etherchannel
interface range f0/2-3
channel-group 1 mode desirable
exit
interface port-channel 1
switchport mode trunk
switchport trunk allow vlan 10,20
switchport trunk native vlan 1000
exit
show interfaces port-channel 1
show etherchannel summary
"""
