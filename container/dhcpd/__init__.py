import tarfile
import time
from io import BytesIO
from ipaddress import IPv4Network
from mininet.link import Link
from container import Docker


class DHCPD(Docker):
    """
        Builds a docker container running a dhcpd daemon
        and creates dhcpd.conf to lease IPs on it's main
        interfaces assinged subnet.

        TODO: Use all linked interfaces
    """

    def __init__(self, name, dhcp_switch, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="dhcpd",
                        **kwargs)

        self.link = Link(self, dhcp_switch)

    def config(self, **kwargs):
        super(DHCPD, self).config(**kwargs)

        # Generates a defauld dhcpd.conf from the link's ip/subnet
        network = IPv4Network(unicode(self.link.intf1.ip + "/" + self.link.intf1.prefixLen), False)
        conf = ("subnet %s netmask %s { }" % (network.network_address, network.netmask)).encode('utf8')

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

        # Run dhcpd on the link's interface
        self.sendCmd("/usr/sbin/dhcpd -d --no-pid %s" % self.link.intf1)
