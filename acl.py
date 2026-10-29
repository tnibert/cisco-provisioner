from functools import reduce
from typing import List, Union

from ip import IPv4Address, IPv6Address
from provisionable import Provisionable, provision_group
from templates.acl import create_named_acl, interface_config, base_standard_rule, base_numbered, base_extended_rule, \
    total_deny_extended, total_deny_standard, total_deny_ipv6, create_ipv6, ipv6_interface_config
from templates.router import INTERFACE_BLOCK

"""
IPv6 strings are in template file, but not implemented here yet.
The commented out tcp_extended_return strings should be made toggleable via a class member.
"""

PERMIT = "permit"
DENY = "deny"
REMARK = "remark"

ACL_TYPE_STANDARD = "standard"
ACL_TYPE_EXTENDED = "extended"

PROTOCOL_TCP = "tcp"

class ACLInterfaceConfig:
    def __init__(self, intf: str, direction: str):
        self.intf = intf
        self.direction = direction

    def get_intf(self):
        return self.intf

    def get_direction(self):
        return self.direction

class ACEStandard(Provisionable):
    def __init__(self, rule: str, source: IPv4Address):
        self.rule = rule # deny, permit, remark
        self.source = source

    def get_source(self):
        return self.source

    def get_rule(self):
        return self.rule

    def provision(self):
        """
        Provision as named modal.  ACL will prepend prefix.
        """
        return base_standard_rule.format(rule=self.get_rule(),
                                         source=self.get_source().get_ip_addr(),
                                         wildcard=self.get_source().get_wildcard_mask())

class ACEExtended(ACEStandard):
    def __init__(self, rule: str, source: IPv4Address, dest: IPv4Address, predicate="", operation="eq", protocol=PROTOCOL_TCP):
        super().__init__(rule, source)
        self.protocol = protocol
        self.dest = dest
        self.op = operation
        self.predicate = predicate

    def get_protocol(self):
        return self.protocol

    def get_destination(self):
        return self.dest

    def provision(self):
        return base_extended_rule.format(rule=self.get_rule(),
                                         protocol=self.get_protocol(),
                                         src=self.get_source().get_ip_addr(),
                                         src_wild=self.get_source().get_wildcard_mask(),
                                         dst=self.get_destination().get_ip_addr(),
                                         dst_wild=self.get_destination().get_wildcard_mask(),
                                         op=self.op,
                                         predicate=self.predicate)

class ACEExtendedIPv6(ACEExtended):
    def __init__(self, rule: str, source: IPv6Address, dest: IPv6Address, predicate="", operation="eq", protocol=PROTOCOL_TCP):
        super().__init__(rule, source, dest, predicate, operation, protocol)

    def provision(self):
        pass

class ACLIPv6(Provisionable):
    def __init__(self,
                 identifier: Union[str | int],
                 interfaces: List[ACLInterfaceConfig],
                 entries: List[ACEExtendedIPv6] = None,
                 deny=False):
        self.interfaces = interfaces
        self.entries = entries if entries is not None else []
        self.identifier = identifier
        self.deny = deny

    def provision_interfaces(self):
        return reduce(lambda a, x: a + x,
                      map(lambda i: INTERFACE_BLOCK.format(intf=i.get_intf(),
                                                           body=ipv6_interface_config.format(
                                                               name=self.identifier,
                                                               direction=i.get_direction())),
                          self.interfaces), "")

    def provision(self):
        return create_ipv6.format(name=self.identifier) + \
            provision_group(self.entries) + \
            (total_deny_ipv6 if self.deny else "") + \
            "end\n" + \
            self.provision_interfaces()

class ACL(Provisionable):
    def __init__(self, identifier: Union[str|int], interfaces: List[ACLInterfaceConfig], entries: List[ACEStandard]=None):
        self.interfaces = interfaces
        self.entries = entries if entries is not None else []
        self.identifier = identifier

    def get_identifier(self):
        return self.identifier

    def provision_interfaces(self) -> str:
        return reduce(lambda a,x: a+x,
                      map(lambda i: INTERFACE_BLOCK.format(intf=i.get_intf(),
                                                           body=interface_config.format(identifier=self.get_identifier(),
                                                                                        direction=i.get_direction())),
                          self.interfaces), "")

class NamedACL(ACL):
    def __init__(self, name: str,
                 interfaces: List[ACLInterfaceConfig],
                 entries: List[ACEStandard]=None,
                 acl_type: str=ACL_TYPE_STANDARD,
                 deny=False):
        super().__init__(name, interfaces, entries)
        self.type = acl_type
        self.deny = deny

    def provision_entries(self) -> str:
        return reduce(lambda a,x: a+x,
                      map(lambda a: "\n" + a.provision(), #\
                                    #+ (named_tcp_extended_return.format(addr=a.get_source().get_ip_addr(),
                                    #                                   wildcard=a.get_source().get_wildcard_mask())
                                    #    if isinstance(a, ACEExtended) and a.get_protocol() == PROTOCOL_TCP else ""),
                          self.entries))

    def total_deny(self) -> str:
        return (total_deny_extended if self.type == ACL_TYPE_EXTENDED else total_deny_standard) if self.deny else ""

    def provision(self):
        return create_named_acl.format(type=self.type, name=self.get_identifier()) \
                + self.provision_entries() + self.total_deny() + self.provision_interfaces()


class NumberedACL(ACL):
    def __init__(self, number: int, interfaces: List[ACLInterfaceConfig], entries: List[ACEStandard]=None):
        super().__init__(number, interfaces, entries)

    def provision_entries(self) -> str:
        return reduce(lambda a,x: a+x,
                      map(lambda a: base_numbered.format(number=self.get_identifier()) + a.provision(), #\
                                    #+ (numbered_tcp_extended_return.format(number=self.identifier,
                                    #                                       addr=a.get_source().get_ip_addr(),
                                    #                                       wildcard=a.get_source().get_wildcard_mask())
                                    #   if isinstance(a, ACEExtended) and a.get_protocol() == PROTOCOL_TCP else ""),
                          self.entries)) #+ base_numbered.format(number=str(self.get_identifier())) + total_deny_extended


    def provision(self):
        return self.provision_entries() + self.provision_interfaces()
