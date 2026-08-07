from templates.common import BASIC_CONFIG

class Device:
    def __init__(self, hostname: str, vty_max: int):
        self.hostname = hostname
        self.vty_max = vty_max

    def provision_basic(self) -> str:
        return BASIC_CONFIG.format(host=self.hostname, vty_max=self.vty_max)
