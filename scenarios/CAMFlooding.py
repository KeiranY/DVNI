"""
CAM Flooding
============
"""

# This import is needed to stop a circular import problem with mininet (https://github.com/mininet/mininet/issues/546)
# noinspection PyUnresolvedReferences
import mininet.node
from mininet.link import TCLink

from controller import PoxController
from scenarios import ArpPoisioning, Scenario
from utils.arp import net_static_arp


class Import(ArpPoisioning.Import):
    """This scenario asks students to flood MAC addresses to force a switch to flood packets. The flooded packets can then be sniffed for login credentials."""

    name = "CAM Table flooding"
    enabled = True
    weight = 50

    def create_network(self, controller=PoxController):
        """Extends the base scenario. Replaces the Kali containers link with a lower bandwidth one. This is so that the flooding attack dosn't cause a Denial of Service for the switch."""
        ArpPoisioning.Import.create_network(self, controller)
        self.connection_wait = 1
        # Remove Kali's link and replace it with a bandwidth limited one
        link = self.kali.defaultIntf().link
        # Get the switch, the switch is whichever node in the link that kali isn't
        switch = link.intf1.node if link.intf2.node is self.kali else link.intf2.node
        self.net.removeLink(link)
        self.net.addLink(switch, self.kali, cls=TCLink, bw=0.25)

    def add_controller(self):
        """Adds a POX controller with the cam_learning switch so that CAM table flooding can be performed against it."""
        self.net.addController(script='cam_learning')

    def run_network(self):
        """Extends the base scenario. Adds static ARP routes so that an ARP poisioning attack wouldn't work for this scenario."""
        super(Import, self).run_network()
        # Add static ARP entries to the hosts
        # This will stop ARP spoofing attacks
        net_static_arp(self.net.hosts)

    def generate_task(self, doc):
        Scenario.generate_task(self, doc)
        doc.add_paragraph(
            'In this scenario your kali machine is connected to a switch capable of learning connected MAC adresses, '
            'this means that traffic will be delivered to the correct device rather than all devices after seeing the device\'s MAC send a packet. ')
        doc.add_paragraph(
            'MAC Addresses in this scenario are learned by storing them in a Content Addressable Memory (CAM) table, a dictionary of MACs to Ports. ')
        doc.add_paragraph(
            'CAM tables such as this one are vulnerable to an attack known as flooding, where by filling the CAM table the switch is forced to relearn the MAC. '
            'Until the MAC address is relearned any packets sent to it are flooded on all of the switches ports, and visable to devices connected to those ports. ')
        doc.add_paragraph(
            'This task requires you to use the \'macof\' to peform CAM Table flooding, then Wireshark/tcpdump can be used to analyse packets. ')
        doc.add_paragraph(
            'NOTE: The macof tool generates a large amount of traffic that slow the network to a crawl like a DOS attack. If you aren\'t succesful in capturing traffic, pause your attack for a bit')
        doc.add_paragraph(
            'Answer the following questions:')


if __name__ == "__main__":
    Import(developer=True, seed="debug").run()
