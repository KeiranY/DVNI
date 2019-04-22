import tarfile
import time
from io import BytesIO

from ipaddress import IPv4Network, IPv4Address

from container import Docker


# TODO: Store and mount the config file rather than copying it, could store in teacher dir https://stackoverflow.com/questions/42248198/how-to-mount-a-single-file-in-a-volume
# TODO: If running and a config change is made restart the server
class Dhcpd(Docker):
    """
        Builds a docker container running a dhcpd daemon
        and creates dhcpd.conf to lease IPs on it's main
        interfaces assinged subnet.
    """

    dhcpd_conf = ""

    def __init__(self, name, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="dhcpd",
                        **kwargs)

    def document(self, doc):
        doc.add_heading('ISC DHCP server', level=2)
        doc.add_paragraph(
            'ISC DHCP server, used in scenarios to enable DHCP starvation or rougue server attacks. To perform these attacks Yersinia is used, available on provided Kali Docker images.')
        doc.add_paragraph("Configuration: \t%s" % self.dhcpd_conf)
        super(Dhcpd, self).document(doc)

    def config(self, **kwargs):
        super(Dhcpd, self).config(**kwargs)
        conf = self.dhcpd_conf.encode('utf-8')
        # Encode conf as tar for use with put_archive
        tarstream = BytesIO()
        tar = tarfile.TarFile(fileobj=tarstream, mode='w')
        tarinfo = tarfile.TarInfo(name='dhcpd.conf')
        tarinfo.size = len(conf)
        tarinfo.mtime = time.time()
        tar.addfile(tarinfo, BytesIO(conf))
        tar.close()
        tarstream.seek(0)

        # Use docker-py's put_archive command to copy our config to the container
        self.dcli.put_archive(self.dc,
                              "/etc/dhcp",
                              tarstream)

        # Run dhcpd on the link's interface NOTE: -d was used previously for debugging

        self.cmd("/usr/sbin/dhcpd  --no-pid %s" % ' '.join(str(intf.name) for idx, intf in self.intfs.items()))

    def add_global(self, option):
        """
            Add global parameter to config. Create these with functions within dhcpd.globals.
        """
        self.dhcpd_conf += option

    def add_subnet(self, ip_network, options=None, addr_range=None):
        # type: (IPv4Network, [str], (IPv4Address, IPv4Address)) -> None
        """
            Add subnet configuration.
            :param ip_network: Network for subnet address and netmask
            :param options: List of options created by functions within dhcpd.options or dhcpd.globals
        """
        # If no address range was supplied, set range to cover every host in the subnet
        if options is None:
            options = []
        if addr_range is None:
            addr_range = (ip_network.network_address + 1, ip_network.broadcast_address - 1)
        # Add address range string to options
        options += ["range %s %s;" % addr_range]
        # Generate subnet configuration and append to config
        self.dhcpd_conf += "subnet %s netmask %s {\n%s\n}" % (
            ip_network.network_address,
            ip_network.netmask,
            '\n'.join(options))
    # Full list of parameters available at: http://www.ipamworldwide.com/ipam/dhcp-server-params.html


def example():
    from mininet.clean import cleanup
    from mininet.cli import CLI
    from mininet.log import info, setLogLevel
    from mininet.net import Containernet
    from container.dhcpd import options

    if __name__ == "__main__":
        setLogLevel('info')

        info('*** Running Cleanup\n')
        cleanup()

        net = Containernet(controller=None)

        info('*** Adding host\n')
        h1 = net.addHost('h1',
                         ip='10.10.10.2/24')
        info('*** Adding switch\n')
        s1 = net.addSwitch('s1')
        info('*** Adding dhcpd\n')
        dhcpd = net.addDocker('dhcpd',
                              cls=Dhcpd,
                              dhcp_switch=s1,
                              ip='10.10.10.1/24')  # type: Dhcpd
        dhcpd.add_subnet(IPv4Network(u'10.10.10.0/24'))
        info('*** Creating links\n')
        net.addLink(h1, s1)
        info('*** Starting network\n')
        net.start()
        info('*** Running CLI\n')
        CLI(net)
        info('*** Stopping network')
        net.stop()


if __name__ == "__main__":
    example()
