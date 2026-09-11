interface_config = """
ip access-group {identifier} {direction}
"""

numbered_rule_config = """
access-list {identifier} {rule} {ip} {wildcard}
"""

create_named_acl = """
ip access-list {type} {name}
"""

modal_named_rule = """
{rule} {source} {wildcard}
"""
