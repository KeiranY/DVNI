"""
Very Secure FTP Daemon
======================
"""
from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Containernet
from mininet.node import Controller

from container import Docker
from utils.account import add_user


class Vsftpd(Docker):
    def __init__(self, name, **kwargs):
        """Creates a Docker container running VSFTPD"""
        Docker.__init__(self,
                        name,
                        dimage="vsftpd",
                        **kwargs)

    def config(self, **kwargs):
        """Extends Node.config. Runs the FTP daemon in the background."""
        super(Vsftpd, self).config(**kwargs)
        self.cmd("vsftpd &")


def example():
    setLogLevel('debug')

    cleanup()

    net = Containernet(controller=Controller)
    net.addController('c0')

    ftp = net.addDocker('ftp',
                        cls=Vsftpd,
                        ip='10.10.10.1/24')
    h1 = net.addHost('h1', ip='10.10.10.2/24')
    s1 = net.addSwitch('s1')
    net.addLink(h1, s1)
    net.addLink(ftp, s1)

    net.start()
    # Add test:test to users
    add_user(ftp, "test", "test")

    CLI(net)
    net.stop()


if __name__ == "__main__":
    example()
