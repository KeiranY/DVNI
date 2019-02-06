from container import Docker


class Kali(Docker):
    def __init__(self, name, resolution="1920x1080x24", port_vnc=5900, port_web=6080, **kwargs):
        if 'environment' not in kwargs:
            kwargs['environment'] = {}
        kwargs['environment']['RESOLUTION'] = resolution
        Docker.__init__(self,
                        name,
                        dimage="kali",
                        ports=[5900, 6080],
                        port_bindings={5900: port_vnc, 6080: port_web},
                        publish_all_ports=True,
                        **kwargs)
