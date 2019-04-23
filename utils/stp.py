"""
Spanning Tree Protocol
=================================
"""
from time import sleep

from mininet.node import OVSSwitch


def wait_STP(switch):
    """
    Waits for STP to be configured on the given switch.
    This is performed by looking for the STP_LEARN status, if the switch is still learning this function waits.

    :type switch: OVSSwitch
    """
    status = switch.dpctl('show')
    while 'STP_FORWARD' not in status or 'STP_LEARN' in status:
        status = switch.dpctl('show')
        sleep(0.5)


class RstpSwitch(OVSSwitch):

    def __init__(self, **kwargs):
        """
        Extenstion class that enables Rapid Spanning Tree protocol.
        """
        super(RstpSwitch, self).__init__(**kwargs)

    def bridgeOpts(self):
        """
        Adds the 'rstp_enable=true' flag to the switches options.
        """
        return super(RstpSwitch, self).bridgeOpts() + ' rstp_enable=true'
