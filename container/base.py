"""
Base Continer
=============
"""

from container import Docker


class Base(Docker):
    """Base docker container, using debian:stretch-slim, that other containers can use."""

    def __init__(self, name, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="base",
                        **kwargs)


def example():
    from mininet.log import setLogLevel
    from mininet.clean import cleanup
    from mininet.net import Containernet
    from mininet.cli import CLI

    setLogLevel('debug')

    cleanup()

    net = Containernet(controller=None)

    base = net.addDocker('base',
                         cls=Base)

    h1 = net.addHost('h1',
                     ip='10.10.10.2/24')
    s1 = net.addSwitch('s1')

    net.addLink(h1, s1)
    net.addLink(base, s1)

    net.start()

    CLI(net)
    net.stop()


if __name__ == "__main__":
    example()
