"""
VLAN Trunking
=============
"""
import random

from container.kali import Kali
from scenarios import Scenario
from utils import subnet
from utils.network import add_switches
from utils.vlan import VlanSwitch, VlanMode


class Import(Scenario):
    name = "VLAN Scanning"
    enabled = True
    weight = 60

    hosts = None
    kali = None  # type: Kali
    switches = None

    def __init__(self, prefixlen=26, vlan_count=3, switch_count=None, host_count=None, vlans=None, **kwargs):
        super(Import, self).__init__(**kwargs)
        self.prefixlen = prefixlen
        self.switch_count = switch_count
        if self.switch_count is None:
            self.switch_count = random.randrange(3, 8)
        self.host_count = host_count
        if self.host_count is None:
            self.host_count = random.randrange(10, 30)
        self.vlans = vlans
        if self.vlans is None:
            vlans = range(1, 10)
            random.shuffle(vlans)
            self.vlans = [vlans.pop() for _ in range(vlan_count)]
            # self.vlans = random_vlans(vlan_count)

    def create_network(self, controller=None):
        super(Import, self).create_network(controller)

        self.hosts = list(subnet.generate(self.prefixlen).hosts())
        random.shuffle(self.hosts)

        # Add switches
        self.switches, switch_links = add_switches(self.net, self.switch_count, cls=VlanSwitch, failMode='standalone')

        # Set native vlan on every inter-switch link
        for link in switch_links:
            for intf in [link.intf1, link.intf2]:
                switch = intf.node  # type: VlanSwitch
                switch.addTag(intf, self.vlans[0])
                switch.addTrunk(intf, *self.vlans)
                switch.addMode(intf, VlanMode.UNTAGGED)

        # Add a kali machine to the first switch in the native VLAN
        self.kali = self.net.addDocker('kali',
                                       cls=Kali,
                                       ip="%s/%s" % (self.hosts.pop(), self.prefixlen))
        kali_link = self.net.addLink(self.switches[0], self.kali)
        self.switches[0].addTag(kali_link.intf1, self.vlans[0])
        self.switches[0].addMode(kali_link.intf1, VlanMode.UNTAGGED)

        # Add a random amount of hosts
        hosts = [self.net.addHost('h' + str(i), ip="%s/%s" % (self.hosts.pop(), self.prefixlen)) for i in
                 range(self.host_count)]

        # Add the hosts to a random switch with a random VLAN
        for host in hosts:
            switch = random.choice(self.switches)
            link = self.net.addLink(switch, host)
            host.vlan = random.choice(self.vlans)
            switch.addTag(link.intf1, host.vlan)
            switch.addMode(link.intf1, VlanMode.ACCESS)  # NOTE: Access is the default mode for ports with a tag

    def run_network(self):
        super(Import, self).run_network()
        if self.developer:
            self.kali.cmd(
                "arp-scan -I %s %s/%s" % (self.kali.defaultIntf(), self.kali.defaultIntf().IP(), self.prefixlen))
            for v in self.vlans:
                self.kali.cmd("arp-scan -I %s -Q %s %s/%s" % (
                    self.kali.defaultIntf(), v, self.kali.defaultIntf().IP(), self.prefixlen))

    def generate_task(self, doc):
        super(Import, self).generate_task(doc)
        doc.add_paragraph("In this scenario your kali machine is part of a network segmented through VLANs. "
                          "However, your Kali machine is connected to a trunk port capable of carrying all VLANs, "
                          "meaning you can communicate with any VLAN by adding a VLAN tag to your packets."
                          "The VLANs are somewhere in the range 1-10. ")
        doc.add_paragraph(
            "The tool arp-scan is able to find devices outside of your VLAN by specifying a VLAN to scan.")
        doc.add_paragraph("Answer the following questions: ")

    def generate_questions(self):
        self.questions += [("What VLANs are active in the network", ' '.join(str(v) for v in self.vlans)),
                           ("What VLAN is the Kali machine connected to. (Hint: scan without a VLAN tag)", str(self.vlans[0])),
                           ("What IP addresses are active on which VLANs", ''.join('\n%s tag %s' % (host.IP(), host.vlan) for host in self.net.hosts if hasattr(host, 'vlan')))]
        # TODO: Add a question asking the user to use vconfig or ip to set their interface VLAN and perform nmap scans on these networks.




if __name__ == "__main__":
    Import(seed="test", developer=True).run()
