from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Containernet
from mininet.node import Controller

from container import Docker


class Ftpd(Docker):
    def __init__(self, name, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="ftpd",
                        **kwargs)

    def config(self, **kwargs):
        super(Ftpd, self).config(**kwargs)
        self.cmd("echo yes > /etc/pure-ftpd/auth/65unix")
        self.cmd("echo yes > /etc/pure-ftpd/conf/UnixAuthentication")
        #self.cmd("pure-ftpd &")


def example():
    setLogLevel('debug')

    cleanup()

    net = Containernet(controller=Controller)
    net.addController('c0')

    ftp = net.addDocker('ftp',
                        cls=Ftpd,
                        ip='10.10.10.1/24')
    h1 = net.addHost('h1', ip='10.10.10.2/24')
    s1 = net.addSwitch('s1')
    net.addLink(h1, s1)
    net.addLink(ftp, s1)

    net.start()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    example()
