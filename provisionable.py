from functools import reduce
from typing import List

from exceptions import Unimplemented


class Provisionable:
    def __init__(self):
        raise Unimplemented("abstract class - use a concrete instance")

    def provision(self):
        raise Unimplemented("need concrete instance of routing protocol")


def provision_group(provisional_group: List[Provisionable]):
    return reduce(lambda a, x: a + x,
                  map(lambda r: r.provision(),
                      provisional_group), "")
