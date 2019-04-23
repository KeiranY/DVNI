"""
Subnet
================
"""

from ipaddress import IPv4Network
import random

# IP address space available for private networks.
privateCIDRs = [IPv4Network(u"10.0.0.0/8"),
                IPv4Network(u"172.16.0.0/12"),
                IPv4Network(u"192.168.0.0/16")]
# Generated networks
# NOTE: 172.17.0.0/16 is used by Docker for internet connection
networks = [IPv4Network(u"172.17.0.0/16")]


def generate(mask, cidr=None):
    """
    Generates an IPv4Network from the given CIDR, or from any of the private addressable ranges if no CIDR is given.

    Example:
        >>> seed(0)
        >>> generate(u"10.0.0.0/8", 24)
        IPv4Network(u'10.216.44.0/24')

    args:
        CIDR (IPv4Network): CIDR range to generate from. Example IPv4Network(u"10.0.0.0/8").
        mask (int): Length in bits to use as host mask.
    """
    # If no cidr is seleted
    if cidr is None:
        # Choose a private CIDR at random
        # from CIDRs with a smaller prefix length than required
        tmp = [c for c in privateCIDRs if c.prefixlen <= mask]
        cidr = random.choice(tmp)

    cidr = IPv4Network(cidr)
    net = _generate(cidr, mask)
    while any(net.overlaps(n) for n in networks):
        net = _generate(cidr, mask)
    networks.append(net)
    return net


def _generate(cidr, mask):
    return IPv4Network(
        (int(cidr.network_address) + (random.getrandbits(int(cidr.hostmask).bit_length() - (32 - mask)) << (32 - mask)), mask))


def overlaps(cidr):
    # type: (IPv4Network) -> bool
    """
    Checks if the given CIDR overlaps with one already generated

    :return: True if overlapping.
    """
    # If any network in networks overlaps with the passed in network
    return any(cidr.overlaps(net) for net in networks)


if __name__ == '__main__':
    while True:
        print(generate(u"10.0.0.0/8", 16))
