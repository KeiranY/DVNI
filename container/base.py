"""
Base Continer
=============
"""

from container import Docker


class Base(Docker):
    """Base docker container, using debian:stretch-slim, that other containers can use."""

    def __init__(self, name, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="base",
                        **kwargs)
