"""
Port Scanning
=============
"""

import random

from ipaddress import IPv4Address

from scenarios import Scenario, HostScanning

# nmap's top 100 port listing
top_100_ports = [7, 9, 13, 21, 22, 23, 25, 26, 37, 53, 79, 80, 81, 88, 106, 110, 111, 113, 119, 135, 139, 143, 144, 179,
                 199, 389, 427, 443, 444, 445, 465, 513, 514, 515, 543, 544, 548, 554, 587, 631, 646, 873, 990, 993,
                 995, 1025, 1026, 1027, 1028, 1029, 1110, 1433, 1720, 1723, 1755, 1900, 2000, 2001, 2049, 2121, 2717,
                 3000, 3128, 3306, 3389, 3986, 4899, 5000, 5009, 5051, 5060, 5101, 5190, 5357, 5432, 5631, 5666, 5800,
                 5900, 6000, 6001, 6646, 7070, 8000, 8008, 8009, 8080, 8081, 8443, 8888, 9100, 9999, 10000, 32768,
                 49152, 49153, 49154, 49155, 49156, 49157]


class Import(HostScanning.Import):
    name = "Port Scanning"
    enabled = True
    weight = 20

    def run_network(self):
        Scenario.run_network(self)
        # Open random top ports for scanning
        for host in self.net.hosts:
            if host.name == 'kali':
                continue
            host.taskPorts = []
            for port in range(0, random.randint(0, 4)):
                host.taskPorts.append(random.choice(top_100_ports))
            # NOTE: May need to pipe 'yes' into this to have some response data
            for port in host.taskPorts:
                host.cmd('nc', '-l', '-d', '-p', port, '&')
        if self.developer:
            self.kali.cmd('ip a')
            self.kali.cmd('nmap -v %s/%s' % (self.kali.defaultIntf().IP(), self.prefixlen))

    def generate_questions(self):
        super(Import, self).generate_questions()
        self.questions.append(("What Port & IP combinations are open on the network",
                               "\n"+("\n".join(
                                   "%s:\t%s" % (
                                        host.IP(),
                                        '\t'.join(str(port) for port in host.taskPorts))
                                   for host in
                                   sorted(self.net.hosts, key=lambda x: int(IPv4Address(x.IP())))
                                   if host.name != 'kali'))))



if __name__ == "__main__":
    # Run network
    Import(developer=True, seed="debug").run()
