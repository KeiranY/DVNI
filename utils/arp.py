"""
Address Routing Protocol
===================================
"""
from mininet.node import Host
from typing import List

# Utility functions intended to help set static ARP routes between hosts.


def net_static_arp(hosts):
    # type: (List[Host]) -> None
    """
    Adds static arp entries from and to every host in the provided list.

    :param hosts: List of hosts.
    """
    # Remove all hosts that lack interfaces
    hosts = [h for h in hosts if h.intfs]
    for src in hosts:
        for dest in hosts:
            if src is not dest:
                _add_entry(src, dest)


def static_arp(host, *hosts_to):
    # type: (Host, List[Host]) -> bool
    """
    Add a static arp entry from "host" to every host in "hosts_to".

    :return Success of adding entry
    :rtype bool
    """
    # If we have no interface it is impossible to add a static arp route
    if not host.intfs:
        return False
    for dest in hosts_to:  # type: Host
        # Don't add ARP entry for the host itself
        if host is dest:
            continue
        # Destination must have at least one interface/ip
        if not dest.intfs:
            continue
        _add_entry(host, dest)
    return True


def _add_entry(src, dest):
    # type: (Host, Host) -> None
    """
    Internal function, runs a command to add a single arp entry from one host to another.
    This function performs no check so is for internal use only.
    """
    src.cmd("arp -i", src.defaultIntf().name, "-s", dest.defaultIntf().IP(), dest.defaultIntf().MAC())
