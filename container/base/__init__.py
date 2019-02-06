from container import Docker


class Base(Docker):
    def __init__(self, name, **kwargs):
        Docker.__init__(self,
                        name,
                        dimage="base",
                        **kwargs)
