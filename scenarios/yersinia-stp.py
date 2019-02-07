#!/usr/bin/python
from time import sleep

from ipaddress import IPv4Address
from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Containernet, OVSSwitch
from mininet.node import Controller
from container.kali import Kali

"""
    Creates a looped topology with OVS's STP enabled switches
    Yersinia on kali can perform attacks on STP
    Run tcpdump on the host machine:
    >>> tcpdump -i any stp
"""

info('*** Running Cleanup\n')
cleanup()

setLogLevel('info')

net = Containernet(controller=Controller)

info('*** Adding controller\n')
net.addController('c0')

ip = IPv4Address(u'10.10.10.0')
inc = 0

info('*** Adding Kali\n')
kali = net.addDocker('kali',
                     cls=Kali,
                     port_vnc=5900,  # OPTIONAL
                     port_web=6080,  # OPTIONAL
                     ip='%s/24' % (ip + (++inc)))

info('*** Adding hosts\n')
hosts = []
for i in range(0, 3):
    hosts.append(net.addHost('h' + str(i), ip='%s/24' % (ip + (++inc))))

info('*** Adding switches\n')
switches = []
for i in range(0, 3):
    switches.append(net.addSwitch('s' + str(i), cls=OVSSwitch, stp=True, failMode='standalone'))
    net.addLink(hosts[i], switches[i])

info('*** Creating links\n')
net.addLink(kali, switches[0])
net.addLink(switches[0], switches[1])
net.addLink(switches[1], switches[2])
net.addLink(switches[2], switches[0])

kali.cmd("apt-get", "install", "-y", "yersinia")

info('*** Starting network\n')
net.start()

info('*** Waiting for STP\n')
for s in net.switches:
    info(s.name + ' ')
    status = s.dpctl('show')
    while 'STP_FORWARD' not in status or 'STP_LEARN' in status:
        status = s.dpctl('show')
        sleep(0.5)
info('\n')

info('*** Running CLI\n')
CLI(net)

info('*** Stopping network')
net.stop()
