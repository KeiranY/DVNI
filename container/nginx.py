"""
Nginx Web Server
=================
"""
from container import Docker


class Nginx(Docker):
    # TODO: just use a base class for containers that don't require extra params
    def __init__(self, name, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="nginx",
                        **kwargs)
