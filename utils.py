import re

format_octet_binary = lambda n: '{0:08b}'.format(n)
strip_blank_lines = lambda s: re.sub(r'^$\n', '', s, flags=re.MULTILINE)
