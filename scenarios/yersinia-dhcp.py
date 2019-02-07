#!/usr/bin/python
from mininet.clean import cleanup
from mininet.log import info, setLogLevel
from mininet.net import Containernet
from mininet.node import Controller

from container.dhcpd import DHCPD
from container.kali import Kali

"""
    Starts a dhcp container and a kali container with yersinia installed
    dhcp logs are outpup on stdout
    running an attack on the server will show the server running out of leases
    >>> yersinia dhcp -attack 1 -interface kali-eth0
"""

info('*** Running Cleanup\n')
cleanup()

setLogLevel('debug')

net = Containernet(controller=Controller)

info('*** Adding controller\n')
net.addController('c0')

info('*** Adding switch\n')
s1 = net.addSwitch('s1')

info('*** Adding docker containers\n')
dhcpd = net.addDocker('dhcpd',
                      cls=DHCPD,
                      dhcp_switch=s1,
                      ip='10.10.10.1/24')
kali = net.addDocker('kali',
                     ip='10.10.10.2/24',
                     cls=Kali)
kali.cmd("apt-get", "install", "-y", "yersinia")

info('*** Creating links\n')
net.addLink(kali, s1)

info('*** Starting network\n')
net.start()

info('*** Running dhcpd in CLI\n')
dhcpd.cmd("/usr/sbin/dhcpd -d --no-pid %s" % dhcpd.link.intf1)

info('*** Stopping network')
net.stop()
