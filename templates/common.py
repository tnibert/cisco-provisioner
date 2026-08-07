BASIC_CONFIG = """
hostname {host}
no ip domain-lookup
enable secret class
line console 0
password cisco
login
logging synchronous
exit
line vty 0 {vty_max}
password cisco
login
logging synchronous
exit
service password-encryption
banner motd $ Authorized Access Only! $
"""

PORT_NO_SHUT = """
no shut
"""
