"""
Docker Containers
=================
"""

import os
import docker
from mininet.log import info, debug
from mininet import node


class Docker(node.Docker):
    """
        Wrapper to mininet.node.Docker that automates building containers. Should be used as the base class for any other docker containers.
    """
    client = docker.from_env()
    built = []
    added = []

    def __init__(self, name, dimage, base='dvni/base', **kwargs):
        self.base_image = base
        # Prepend image names with our repo name
        dimage = 'dvni/' + dimage
        # Build the needed image if it doesn't exist
        if dimage not in Docker.built:
            self.build(dimage)
        super(Docker, self).__init__(name, dimage, **kwargs)
        Docker.added.append(self)

    def document(self, doc):
        # Derived classes should implement this to write documentation about themselves
        # By default prints interfaces if they exist
        if self.intfs:
            p = doc.add_paragraph()
            for key, intf in self.intfs.items():
                p.add_run('Interface: \t%s\n' % str(intf.name)).bold = True
                p.add_run('IP Address: \t%s/%s\n' % (str(intf.ip), str(intf.prefixLen)))
                p.add_run('MAC: \t\t%s\n\n' % str(intf.mac))
        pass

    def build(self, name):
        """
            Build dockerfile from the container/ directory

            Example:
                >>> self.build("kali")
                (<Image: 'dvni/kali:latest'>, <itertools.tee object at 0x7f8c1d698098>)

            Args:
                name (str): The directory within container/ containing the Dockerfilr

            Returns:
                (:py:class:`Image`): The built image.

        """
        if name is not self.base_image:
            # if base image isn't built
            if not Docker.client.images.list(name=self.base_image):
                # Build base image
                self.build(self.base_image)

        print('*** Building ' + name + ' docker container\n')
        # If path to Dockerfile doesn't exist
        path = os.path.dirname(os.path.realpath(__file__)) + "/" + name[5:]
        if not os.path.isdir(path):
            # Raise exception with path for clarity
            raise Exception("Container does not exist: path = %s" % path)

        image = Docker.client.images.build(path=path,
                                           rm=True)
        if len(image.tags) == 0:
            image.tag(name)
        # If the log level is debug, print the build log
        #for line in logs:
        #    debug(line)
        # Add this image to the built list
        Docker.built.append(name)
        return name
