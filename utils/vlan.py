import random
from enum import Enum
from mininet.link import Intf
from mininet.node import OVSSwitch
from typing import Dict, List


class VlanMode(Enum):
    ACCESS = 'access'
    TRUNK = 'trunk'
    TAGGED = 'native-tagged'
    UNTAGGED = 'native-untagged'


# Generate random VLAN numbers from 2 to 0xFFE
# since 0 & 0xFFF are reserved VLANs and 1 is native
vlans = range(2, 0xFFE)
random.shuffle(vlans)


def random_vlan():
    return vlans.pop()


def random_vlans(count):
    return [vlans.pop() for _ in range(count)]


def _cmd_intf(cmd, intf):
    """
    Passes the given command to Virtual Switch control (ovs-vsctl), configures an OVSSwitch

    :param cmd: Command to pass to vsctl.
            Contains one unformatted '%s' to be replaced with interface name
    :param intf: The interface to run the command with
    :return:
    """
    intf.node.vsctl(cmd % intf)


def tag_intf(intf, tag):
    """
    Adds the given VLAN tag to OVSSwitch ports.

    :param intf: The interface to tag.
    :param tag: The VLAN tag to add
    :return:
    """
    _cmd_intf('set port %s tag=' + str(tag), intf)
    return intf


def trunk_intf(intf, trunks):
    """
    Adds the given VLAN trunks to an OVSSwitch port.

    :param intf: The interface to add trunks to.
    :param trunks:
    """
    _cmd_intf('set port %s trunks=' + ','.join(str(x) for x in trunks), intf)


def vlan_mode_intf(intf, mode=VlanMode.UNTAGGED):
    # type: (Intf, VlanMode) -> None
    """
    Sets the VLAN mode for an OVSSwitch port.

    :param intf: The interface to set VLAN mode on.
    :param mode: 'native-tagged' or 'native-untagged'
    :return:
    """
    _cmd_intf('set port %s vlan_mode=' + mode.value, intf)


class VlanSwitch(OVSSwitch):
    trunks = dict()  # type: Dict[Intf, List[int]]
    tags = dict()  # type: Dict[Intf, int]
    modes = dict()  # type: Dict[Intf, VlanMode]

    def addTrunk(self, intf, *trunks):
        # type: (Intf, List[int]) -> None
        # Append trunks if some already exist
        if intf in self.trunks:
            self.trunks[intf] += trunks
        else:
            self.trunks[intf] = trunks

    def addTag(self, intf, tag):
        # type: (Intf, int) -> None
        self.tags[intf] = tag

    def addMode(self, intf, mode=VlanMode.UNTAGGED):
        # type: (Intf, VlanMode) -> None
        self.modes[intf] = mode

    def start(self, controllers):
        super(VlanSwitch, self).start(controllers)
        # Add VLAN trunks to OVSSwitch ports
        [trunk_intf(intf, trunks) for intf, trunks in self.trunks.items()]
        # Add VLAN tag to OVSSwitch ports
        [tag_intf(intf, tag) for intf, tag in self.tags.items()]
        # Sets the VLAN mode for OVSSwitch ports
        [vlan_mode_intf(intf, mode) for intf, mode in self.modes.items()]
