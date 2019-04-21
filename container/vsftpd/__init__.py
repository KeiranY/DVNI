import random
from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Containernet
from mininet.node import Controller

from container import Docker


class Vsftpd(Docker):
    def __init__(self, name, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="vsftpd",
                        **kwargs)

    def config(self, **kwargs):
        super(Vsftpd, self).config(**kwargs)
        self.cmd("vsftpd &")

    def add_user(self, username=None, password=None):
        if not password:
            password = '%020x' % random.randrange(16 ** 20)
        # Add a user for ftp
        self.cmd("adduser", "--disabled-password", "--gecos", '""', username)
        self.cmd('echo', "'%s:%s'" % (username, password), '|', 'chpasswd')


if __name__ == "__main__":
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
    ftp.cmd("adduser", "--disabled-password", "--gecos", '""', "test")
    ftp.cmd('echo', "'%s:%s'" % ("test", "test"), '|', 'chpasswd')

    CLI(net)
    net.stop()
