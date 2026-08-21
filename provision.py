#! /usr/bin/env python3

import sys
import importlib


if __name__=='__main__':
    """
    generate provisioning commands
    """
    if len(sys.argv) > 1:
        devices = importlib.import_module(sys.argv[1]).devices
    else:
        sys.exit("error: must specify description module\neg:\n./provision.py examples.example1")

    if len(sys.argv) > 2:
        # provision specific device
        print(devices[sys.argv[2]].provision())
    else:
        # all
        for k,v in devices.items():
            config = v.provision()
            print(f"-----{k}-----")
            print(config)
