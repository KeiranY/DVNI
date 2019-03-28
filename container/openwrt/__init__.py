from container import Docker


class Openwrt(Docker):
    """
        Creates an OpenWRT router.

        args:
            resolution (str, optional): Build version of OpenWRT to use. https://downloads.openwrt.org/releases/
    """

    def __init__(self, name, version=None, **kwargs):
        if version is not None:
            if 'environment' not in kwargs:
                kwargs['environment'] = {}
            kwargs['environment']['OPENWRT_VERSION'] = version
        Docker.__init__(self,
                        name,
                        dcmd='/sbin/init',
                        dimage="openwrt",
                        ports=[80], # For debugging
                        port_bindings={80: 80},
                        **kwargs)

    def config(self, **kwargs):
        super(Openwrt, self).config(**kwargs)
        # Since BusyBox's ifconfig doesn't support the CIDR notation
        # used by containernet to set IPs, use the ip command here to
        # set OpenWRT's interfaces ourselves
        # TODO: It may be worthwhile forking containernet to use ip over ifconfig
        self.cmd("echo config interface lan >> /etc/config/network")
        options = [('ifname', ' '.join([intf.name for key, intf in self.intfs.items()])),
                   ('type', 'bridge'),
                   ('proto', 'static'),
                   ('ipaddr', self.intfs[0].ip),
                   ('netmask', '.'.join(
                       [str((0xffffffff << (32 - int(self.intfs[0].prefixLen)) >> i) & 0xff) for i in [24, 16, 8, 0]]))]
        for opt, value in options:
            self.cmd("echo \"    option %s '%s'\"" % (opt, value) + " >> /etc/config/network")



def example():
    from mininet.clean import cleanup
    from mininet.cli import CLI
    from mininet.log import info, setLogLevel
    from mininet.net import Containernet
    from mininet.node import Controller
    from container.kali import Kali
    setLogLevel('debug')

    info('*** Running Cleanup\n')
    cleanup()

    net = Containernet(controller=Controller)
    net.addController('c0')

    info('*** Adding Kali\n')
    kali = net.addDocker('kali',
                         cls=Kali,
                         ip='10.10.10.1/24')
    info('*** Adding openwrt\n')
    openwrt = net.addDocker('openwrt',
                            cls=Openwrt,
                            ip='10.10.10.2/24')
    info('*** Adding switch\n')
    s1 = net.addSwitch('s1')
    info('*** Creating links\n')
    net.addLink(kali, s1)
    net.addLink(openwrt, s1)
    info('*** Starting network\n')
    net.start()
    info('*** Running CLI\n')
    CLI(net)
    info('*** Stopping network')
    net.stop()


if __name__ == "__main__":
    example()
