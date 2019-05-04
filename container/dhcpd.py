"""
ISC DHCP Server
===============
"""
import tarfile
import time
from io import BytesIO

from ipaddress import IPv4Network, IPv4Address

from container import Docker


class Dhcpd(Docker):

    def __init__(self, name, **kwargs):
        """
        Docker container running a DHCP Daemon

        Attributes:
            conf: String storing dhcpd.conf settings.
        """
        Docker.__init__(self,
                        name,
                        dimage="dhcpd",
                        **kwargs)
        self.conf = ""  # type: str
        self.dhcp_pid = None

    def document(self, doc):
        doc.add_heading('ISC DHCP server', level=2)
        doc.add_paragraph(
            'ISC DHCP server, used in scenarios to enable DHCP starvation or rougue server attacks. To perform these attacks Yersinia is used, available on provided Kali Docker images.')
        doc.add_paragraph("Configuration: \t%s" % self.conf)
        super(Dhcpd, self).document(doc)

    def config(self, **kwargs):
        """
        Extends Node.config. Creates a file containing the settings from 'conf' and writes them to /etc/dhcp inside the container.

        TODO:
            If running and a config change is made restart the server

        TODO:
            Store and mount the config file rather than copying it https://stackoverflow.com/questions/42248198/how-to-mount-a-single-file-in-a-volume
        """

        super(Dhcpd, self).config(**kwargs)
        conf = self.conf.encode('utf-8')
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

        self.dhcp_pid = self.cmd("/usr/sbin/dhcpd  --no-pid %s" % ' '.join(str(intf.name) for idx, intf in self.intfs.items()))

    def add_global(self, option):
        # type: (str) -> None
        """
        Add global parameter to 'conf'. Create these with functions within dhcpd.globals.
        :param option: String returned from one of the methods inside 'dhcpd.globals' class.
        """
        self.conf += option

    def add_subnet(self, ip_network, option_list=None, addr_range=None):
        # type: (IPv4Network, [str], (IPv4Address, IPv4Address)) -> None
        """
            Adds a subnet configuration with the supplied parameters to 'conf'.

            :param ip_network: Network for subnet address and netmask.
            :param addr_range: Range of IP addresses the DHCP server will assign.
            :param option_list: List of options created by functions within 'dhcpd.options' or 'dhcpd.globals'.
        """
        # If no address range was supplied, set range to cover every host in the subnet
        if option_list is None:
            option_list = []
        if addr_range is None:
            addr_range = (ip_network.network_address + 1, ip_network.broadcast_address - 1)
        # Add address range string to options
        option_list += ["range %s %s;" % addr_range]
        # Generate subnet configuration and append to config
        self.conf += "subnet %s netmask %s {\n%s\n}" % (
            ip_network.network_address,
            ip_network.netmask,
            '\n'.join(option_list))
    # Full list of parameters available at: http://www.ipamworldwide.com/ipam/dhcp-server-params.html


# noinspection PyClassHasNoInit
class globals:
    """
    Global options as per http://www.ipamworldwide.com/ipam/dhcp-server-params.html.
    NOTE: not all options are implemented.
    """

    @staticmethod
    def authoritative():
        return "authoritative;"

    @staticmethod
    def local_port(port):
        # type: (int) -> str
        if port not in range(1, 65536):
            raise IndexError("TCP Port must be between 1 and 65535 inclusive.")
        return "local-port %s;" % str(port)

    @staticmethod
    def local_address(address):
        # type: (IPv4Address) -> str
        return "local-address %s;" % str(address)

    @staticmethod
    def default_lease_time(time):
        # type: (int) -> str
        return "default-lease-time %s;" % str(time)

    @staticmethod
    def min_lease_time(time):
        # type: (int) -> str
        return "min-lease-time %s;" % str(time)

    @staticmethod
    def max_lease_time(time):
        # type: (int) -> str
        return "max-lease-time %s;" % str(time)


# noinspection PyClassHasNoInit
class options:
    """
    Per network options as per http://www.ipamworldwide.com/ipam/isc-dhcpv4-options.html
    NOTE: not all options are implemented.
    """
    from typing import List, Tuple

    @staticmethod
    def subnet_mask(ip_network):
        # type: (IPv4Network) -> str
        return "option subnet-mask %s;" % str(ip_network.netmask)

    @staticmethod
    def broadcast_address(ip_network):
        # type: (IPv4Network) -> str
        return "option broadcast-address %s;" % str(ip_network.broadcast_address)

    @staticmethod
    def _server_list(name, *addresses):
        """
            Internal helper function for options which are lists of addresses.
        """
        return "option %s %s;" % (name, ' '.join([str(address) for address in addresses]))

    @staticmethod
    def routers(*addresses):
        # type: (List[IPv4Address]) -> str
        return options._server_list("routers", addresses)

    @staticmethod
    def time_servers(*addresses):
        # type: (List[IPv4Address]) -> str
        return options._server_list("time-servers", addresses)

    @staticmethod
    def domain_name(name):
        # type: (str) -> str
        return "option domain-name %s;" % name

    @staticmethod
    def domain_name_servers(*addresses):
        # type: (List[IPv4Address]) -> str
        return options._server_list("domain-name-servers", addresses)

    @staticmethod
    def log_servers(*addresses):
        # type: (List[IPv4Address]) -> str
        return options._server_list("log-servers", addresses)

    @staticmethod
    def cookie_servers(*addresses):
        # type: (List[IPv4Address]) -> str
        return options._server_list("cookie-servers", addresses)

    @staticmethod
    def ntp_servers(*addresses):
        # type: (List[IPv4Address]) -> str
        return options._server_list("ntp-servers", addresses)

    @staticmethod
    def router_discovery(should_discover):
        # type: (bool) -> str
        return "option routers %s;" % str(should_discover).lower()

    @staticmethod
    def static_routes(*addresses):
        # type: ([Tuple[IPv4Address, IPv4Address]]) -> str
        return "option domain_name_servers %s;" % ','.join(["%s, %s" % (addr1, addr2) for addr1, addr2 in addresses])


def example():
    from mininet.clean import cleanup
    from mininet.cli import CLI
    from mininet.log import info, setLogLevel
    from mininet.net import Containernet

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
        net.addLink(dhcpd, s1)
        info('*** Starting network\n')
        net.start()
        info('*** Running CLI\n')
        CLI(net)
        info('*** Stopping network')
        net.stop()


if __name__ == "__main__":
    example()
