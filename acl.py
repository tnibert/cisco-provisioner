from functools import reduce
from typing import List, Union

from ip import IPv4Address
from provisionable import Provisionable
from templates.acl import create_named_acl, modal_named_rule, interface_config, numbered_rule_config
from templates.router import INTERFACE_BLOCK


PERMIT = "permit"
DENY = "deny"
REMARK = "remark"

class ACLInterfaceConfig:
    def __init__(self, intf: str, direction: str):
        self.intf = intf
        self.direction = direction

    def get_intf(self):
        return self.intf

    def get_direction(self):
        return self.direction

class ACE:
    def __init__(self, rule, source: IPv4Address):
        self.rule = rule # deny, permit, remark
        self.source = source

    def get_addr(self):
        return self.source.get_ip_addr()

    def get_wildcard(self):
        return self.source.get_wildcard_mask()

    def get_rule(self):
        return self.rule

    def get_modal_named_rule(self):
        return modal_named_rule.format(rule=self.get_rule(),
                                       source=self.get_addr(),
                                       wildcard=self.get_wildcard())

class ACL(Provisionable):
    def __init__(self, identifier: Union[str|int], interfaces: List[ACLInterfaceConfig], entries: List[ACE]=None):
        self.interfaces = interfaces
        self.entries = entries if entries is not None else []
        self.identifier = identifier

    def provision_interfaces(self) -> str:
        return reduce(lambda a,x: a+x,
                      map(lambda i: INTERFACE_BLOCK.format(intf=i.get_intf(),
                                                           body=interface_config.format(identifier=self.identifier,
                                                                                        direction=i.get_direction())),
                          self.interfaces))

class NamedACL(ACL):
    def __init__(self, name: str, interfaces: List[ACLInterfaceConfig], entries: List[ACE]=None):
        super().__init__(name, interfaces, entries)

    def provision_entries(self) -> str:
        return reduce(lambda a,x: a+x,
                      map(lambda a: a.get_modal_named_rule(),
                          self.entries))

    def provision(self):
        return create_named_acl.format(type="standard", name=self.identifier) \
                + self.provision_entries() + "deny any\n" + self.provision_interfaces()

class NumberedACL(ACL):
    def __init__(self, number: int, interfaces: List[ACLInterfaceConfig], entries: List[ACE]=None):
        super().__init__(number, interfaces, entries)

    def provision_entries(self) -> str:
        return reduce(lambda a,x: a+x,
                      map(lambda a: numbered_rule_config.format(
                              identifier=self.identifier,
                              rule=a.get_rule(),
                              ip=a.get_addr(),
                              wildcard=a.get_wildcard()
                          ),
                          self.entries)) + "access-list " + str(self.identifier) + " deny any"


    def provision(self):
        return self.provision_entries() + self.provision_interfaces()
