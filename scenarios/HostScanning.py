import random

from docx import Document
from ipaddress import IPv4Address
from mininet.node import Controller

from utils import subnet
from container.kali import Kali
from scenarios import Scenario


class Import(Scenario):
    name = "Host Scanning"
    enabled = True
    weight = 10

    kali = None  # type: Kali
    subnet = None
    prefixlen = None

    def create_network(self, controller=Controller):
        Scenario.create_network(self, controller)
        # Add switch
        switch = self.net.addSwitch('s1')
        # Create a random subnet to add hosts to
        self.prefixlen = random.randint(24, 27)
        self.subnet = subnet.generate(self.prefixlen)
        hosts = list(self.subnet.hosts())
        # Add kali
        self.kali = self.net.addDocker('kali',
                                       cls=Kali,
                                       ip="%s/%s" % (hosts.pop(), self.prefixlen))
        self.net.addLink(switch, self.kali)
        for i in range(0, random.randint(10, 25)):
            # If the host list is empty, exit
            if not hosts:
                break
            # Get a random IP from the list of hosts
            ip = hosts.pop(random.randrange(len(hosts)))
            # Add a host
            host = self.net.addHost('h' + str(i), ip="%s/%s" % (ip, self.prefixlen))
            # Link host to switch
            self.net.addLink(switch, host)

    def run_network(self):
        super(Import, self).run_network()
        if self.developer:
            self.kali.cmd('ip a')
            self.kali.cmd('nmap -v %s/%s' % (self.kali.defaultIntf().IP(), self.prefixlen))

    def generate_task(self, doc):
        super(Import, self).generate_task(doc)
        doc.add_paragraph(
            'This task requires you to use ip/ifconfig and nmap to gather information about the connected network. answer the following quenstions:')

    def generate_questions(self):
        self.questions += [("What subnet is assigned to the Kali machine", str(self.kali.defaultIntf().IP())),
                           ("What is the Network Address of this network", str(self.subnet.network_address)),
                           ("What is the Broadcast Address of this network", str(self.subnet.broadcast_address)),
                           ("What Range of IP adresses is usable in this subnet", "%s - %s" % (self.subnet.network_address + 1, self.subnet.broadcast_address - 1)),
                           # Sort by IP, don't include Kali
                           ("What IP adresses are found to have hosts up", "\n"+("\n".join(
                               host.IP() for
                               host in sorted(self.net.hosts, key=lambda x: int(IPv4Address(x.IP())))
                               if host.name != 'kali')))]


if __name__ == "__main__":
    # Run network
    Import(developer=True, seed="debug").run()
