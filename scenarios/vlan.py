#!/usr/bin/python
from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Containernet, OVSSwitch
from mininet.node import NullController
from examples.vlanhost import VLANHost
from container.kali import Kali

"""
    Example network with hosts tagging their own VLANs
"""

info('*** Running Cleanup\n')
cleanup()

setLogLevel('info')

net = Containernet(controller=NullController)

info('*** Adding kali\n')
kali = net.addDocker('kali',
                     cls=Kali,
                     ip='10.10.10.5/24')

info('*** Adding hosts\n')
h1 = net.addHost('h1', ip='10.10.10.1/24', cls=VLANHost, vlan=10)
h2 = net.addHost('h2', ip='10.10.10.2/24', cls=VLANHost, vlan=10)
h3 = net.addHost('h3', ip='10.10.10.3/24', cls=VLANHost, vlan=20)
h4 = net.addHost('h4', ip='10.10.10.4/24', cls=VLANHost, vlan=20)

info('*** Adding switch\n')
s1 = net.addSwitch('s1', cls=OVSSwitch, failMode='standalone')
s2 = net.addSwitch('s2', cls=OVSSwitch, failMode='standalone')

info('*** Creating links\n')
net.addLink(kali, s1)
l1 = net.addLink(h1, s1).intf2
l2 = net.addLink(h2, s2).intf2
l3 = net.addLink(h3, s1).intf2
l4 = net.addLink(h4, s2).intf2

info('*** Starting network\n')
net.start()

info('*** Configuring Kali VLAN\n')
intf = kali.defaultIntf()
kali.cmd('ip link add link %s name %s.10 type vlan id 10' % (intf, intf))
kali.cmd('ip addr del %s dev %s' % (kali.params['ip'], intf))
kali.cmd('ip addr add %s dev %s.10' % (kali.params['ip'], intf))
kali.cmd('ip link set dev %s.10 up' % intf)
kali.cmd('ip -d a')

info('*** Running CLI\n')
CLI(net)

info('*** Stopping network')
net.stop()
