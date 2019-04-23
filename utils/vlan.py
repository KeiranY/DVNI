"""
Virtual LAN
=====================
"""
import random
from enum import Enum
from mininet.link import Intf
from mininet.node import OVSSwitch
from typing import Dict, List


class VlanMode(Enum):
    """
    Enum for the types of VLAN mode in Open vSwitch. See: http://www.openvswitch.org/support/dist-docs/ovs-vswitchd.conf.db.5.html
    """
    ACCESS = 'access'
    TRUNK = 'trunk'
    TAGGED = 'native-tagged'
    UNTAGGED = 'native-untagged'
    TUNNEL = 'dot1q-tunnel'


vlans = None
"""Stores unused VLANs in a random order for use with the utility functions.
   Generated the first time a VLAN is requested. 
   Originally holds numbers from 1 to 0xFFE since 0 & 0xFFF are reserved VLANs"""


def _generate_vlans():
    global vlans
    vlans = range(1, 0xFFE)
    random.shuffle(vlans)


def random_vlan():
    # type: () -> int
    """Returns a random unused VLAN"""
    if not vlans:
        _generate_vlans()
    return vlans.pop()


def random_vlans(count):
    # type: (int) -> List[int]
    """Returns 'count' amount of random unused VLANs"""
    if not vlans:
        _generate_vlans()
    return [vlans.pop() for _ in range(count)]


def _cmd_intf(cmd, intf):
    """
    Passes the given command to Virtual Switch control (ovs-vsctl), configures an OVSSwitch.

    :param cmd: Command to pass to vsctl.
            Contains one unformatted '%s' to be replaced with interface name
    :param intf: The interface to run the command with
    """
    intf.node.vsctl(cmd % intf)


def tag_intf(intf, tag):
    """
    Sets the VLAN tag of an OVSSwitch port.

    :param intf: The interface to tag.
    :param tag: The VLAN tag to add
    """
    _cmd_intf('set port %s tag=' + str(tag), intf)


def trunk_intf(intf, trunks):
    # type: (Intf, List[int]) -> None
    """
    Adds the VLAN trunks to an OVSSwitch port.

    :param intf: The interface to add trunks to.
    :param trunks: List of trunks to add.
    """
    _cmd_intf('set port %s trunks=' + ','.join(str(x) for x in trunks), intf)


def vlan_mode_intf(intf, mode=VlanMode.UNTAGGED):
    # type: (Intf, VlanMode) -> None
    """
    Sets the VLAN mode of an OVSSwitch port.

    :param intf: The interface to set VLAN mode on.
    :param mode: The mode to set.
    :return:
    """
    _cmd_intf('set port %s vlan_mode=' + mode.value, intf)


class VlanSwitch(OVSSwitch):

    def __init__(self, **kwargs):
        """
        Adds extension functions to OVSSwitch for the management of VLAN settings.
        """
        super(VlanSwitch, self).__init__(**kwargs)
        self.trunks = dict()
        self.tags = dict()
        self.modes = dict()

    def addTrunk(self, intf, *trunks):
        # type: (Intf, List[int]) -> None
        """Adds VLAN trunks to an interface."""
        # Append trunks if some already exist
        if intf in self.trunks:
            self.trunks[intf] += trunks
        else:
            self.trunks[intf] = trunks

    def addTag(self, intf, tag):
        # type: (Intf, int) -> None
        """Sets VLAN tag of an interface."""
        self.tags[intf] = tag

    def addMode(self, intf, mode=VlanMode.UNTAGGED):
        # type: (Intf, VlanMode) -> None
        """Sets VLAN mode of an interface."""
        self.modes[intf] = mode

    def start(self, controllers):
        """Extends OVSSwitch function. Sets VLAN settings at start-time."""
        super(VlanSwitch, self).start(controllers)
        # Add VLAN trunks to OVSSwitch ports
        [trunk_intf(intf, trunks) for intf, trunks in self.trunks.items()]
        # Add VLAN tag to OVSSwitch ports
        [tag_intf(intf, tag) for intf, tag in self.tags.items()]
        # Sets the VLAN mode for OVSSwitch ports
        [vlan_mode_intf(intf, mode) for intf, mode in self.modes.items()]
