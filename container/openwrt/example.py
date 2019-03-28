from mininet.clean import cleanup
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Containernet
from mininet.node import Controller
from container.kali import Kali
from container.openwrt import Openwrt

setLogLevel('debug')

info('*** Running Cleanup\n')
cleanup()

net = Containernet(controller=None)

info('*** Adding Kali\n')
kali = net.addDocker('kali',
                     cls=Kali,
                     ip=None)
h1 = net.addHost('h1', ip=None)
info('*** Adding openwrt\n')
openwrt = net.addDocker('openwrt',
                        cls=Openwrt,
                        ip=None)
info('*** Creating links\n')
link = net.addLink(kali, openwrt)
link.intf1.setIP('10.10.10.1', '24')
link.intf2.setIP('10.10.10.3', '24')

link = net.addLink(h1, openwrt)
link.intf1.setIP('10.10.10.2', '24')
link.intf2.setIP('10.10.10.4', '24')

info('*** Starting network\n')
net.start()
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
