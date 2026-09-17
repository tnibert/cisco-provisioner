interface_config = """
ip access-group {identifier} {direction}
"""

base_numbered = "\naccess-list {number} "
base_standard_rule = "{rule} {source} {wildcard}\n"

numbered_rule_config = base_numbered + base_standard_rule

create_named_acl = """
ip access-list {type} {name}
"""

modal_named_rule = "\n" + base_standard_rule

base_extended_rule = "{rule} {protocol} {src} {src_wild} {dst} {dst_wild} {op} {predicate}\n"
base_tcp_extended_return = "permit tcp any {addr} {wildcard} established\n"

numbered_extended_rule = base_numbered + base_extended_rule

numbered_tcp_extended_return = base_numbered + base_tcp_extended_return

modal_named_extended_rule = "\n" + base_extended_rule

named_tcp_extended_return = "\n" + base_tcp_extended_return

ipv6_interface_config = """
ipv6 traffic-filter {name} {direction}
"""

total_deny_standard = "deny any\n"
total_deny_extended = "deny ip any any\n"
total_deny_ipv6 = "deny ipv6 any any\n"
