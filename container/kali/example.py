#!/usr/bin/python
from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Containernet
from mininet.node import Controller
from container.kali import Kali

"""
    Run a network with a kali container and a mininet host
"""
if __name__ == "__main__":
    setLogLevel('info')

    info('*** Running Cleanup\n')
    cleanup()

    net = Containernet(controller=Controller)
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding Kali\n')
    kali = net.addDocker('kali',
                         cls=Kali,
                         resolution="1920x1080x24",  # OPTIONAL
                         port_vnc=5900,  # OPTIONAL
                         port_web=6080,  # OPTIONAL
                         ip='10.10.10.1/24')

    info('*** Adding host\n')
    h1 = net.addHost('h1',
                     ip='10.10.10.2/24')

    info('*** Adding switch\n')
    s1 = net.addSwitch('s1')

    info('*** Creating links\n')
    net.addLink(h1, s1)
    net.addLink(kali, s1)

    info('*** Starting network\n')
    net.start()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()
