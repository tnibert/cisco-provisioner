import sys

from examples.example1 import devices

format_octet_binary = lambda n: '{0:08b}'.format(n)


if __name__=='__main__':
    """
    generate provisioning commands
    """
    if len(sys.argv) > 1:
        # provision specific device
        print(devices[sys.argv[1]].provision())
    else:
        # all
        for k,v in devices.items():
            config = v.provision()
            print(f"-----{k}-----")
            print(config)
