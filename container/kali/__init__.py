from container import Docker


class Kali(Docker):
    """
        Creates a Kali host running a VNC server and NoVNC web server

        args:
            resolution (str, optional): String in the format XxYxDepth for the remote display. Defaults to 1920x1080x24
            vnc (int, optional): Port to bind VNC to on the host. Defaults to 5900
            web (int, options): Port to bind NoVNC to on the host. Defaults to 6080
    """
    def __init__(self, name, resolution="1920x1080x24", vnc=5900, web=6080, **kwargs):
        if 'environment' not in kwargs:
            kwargs['environment'] = {}
        kwargs['environment']['RESOLUTION'] = resolution
        Docker.__init__(self,
                        name,
                        dimage="kali",
                        ports=[5900, 6080],
                        port_bindings={5900: vnc, 6080: web},
                        publish_all_ports=True,
                        **kwargs)
