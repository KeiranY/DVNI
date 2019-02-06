import os
import docker
from mininet.log import info, debug
from mininet import node


class Docker(node.Docker):
    """
        Wrapper to mininet.node.Docker that automates building containers
    """
    client = docker.from_env()
    built = []

    def __init__(self, name, dimage, **kwargs):
        # Prepend image names with our repo name
        dimage = 'dvni/' + dimage
        # Build the needed image if it doesn't exist
        if dimage not in Docker.built:
            self.build(dimage)

        super(Docker, self).__init__(name, dimage, **kwargs)

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
        # if base image isn't built
        if name is not "dvni/base":
            if not Docker.client.images.get("dvni/base"):
                # Build base image
                self.build("dvni/base")

        info('*** Building ' + name + ' docker container\n')
        # If path to Dockerfile doesn't exist
        path = os.path.dirname(os.path.realpath(__file__)) + "/" + name[5:]
        if not os.path.isdir(path):
            # Raise exception with path for clarity
            raise Exception("Container does not exist: path = %s" % path)
        image, logs = Docker.client.images.build(path=path,
                                                 tag=name,
                                                 rm=True)
        # If the log level is debug, print the build log
        for line in logs:
            debug(line)
        # Add this image to the built list
        Docker.built.append(name)
        return name
