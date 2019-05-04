"""
ARP Poisoning
=============
"""

from mininet.node import Controller

from scenarios import PacketSniffing, Scenario


class Import(PacketSniffing.Import):
    """This scenario requires the user to perform ARP poisioning to force other hosts on the network to send traffic to them. This traffic can then be sniffed for login credentials."""

    name = "ARP Poisoning"
    enabled = True
    weight = 40

    def create_network(self, controller=Controller):
        self.packages += ["ettercap-graphical", "dsniff"]
        PacketSniffing.Import.create_network(self, controller)

    def run_network(self):
        Scenario.run_network(self)
        self.add_ftp()

    def add_switch(self):
        self.switch = self.net.addSwitch('s1')

    def generate_task(self, doc):
        Scenario.generate_task(self, doc)
        doc.add_paragraph(
            'In this scenario your kali machine is connected to a switch capable of learning connected MAC adresses, '
            'this means that traffic will be delivered to the correct device once it\'s location has been learned.')
        doc.add_paragraph(
            'This task requires you to use ettercap/arpspoof to trick devices into sending traffic to you instead of the intended recipient, '
            'then Wireshark/tcpdump can be used to analyse packets.')
        doc.add_paragraph(
            'Answer the following questions:')


if __name__ == "__main__":
    # Run network
    Import(developer=True, seed="debug").run()
