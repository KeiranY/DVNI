"""
Controllers
===========
"""

import os
from shutil import copyfile

from mininet.node import Controller
from typing import Dict


class PoxController(Controller):

    pox_directory = "/var/pox"
    """The installaction diretory of POX"""

    pox_comand = pox_directory + '/pox.py'
    """The location of 'pox.py'"""

    def __init__(self, name, script, verbose=False, **kwargs):
        # type: (str, str, bool, Dict) -> None
        """
        POX OpenFlow controller implementation for Mininet. Allows scripts within this folder to act as a controller for OpenFlow based switches.

        :param name: Controller name for Mininet
        :param script: Filename of the script to
        :param verbose: Passes '--verbose' flag to pox.py
        """

        PoxController.copyScript(script)
        Controller.__init__(self, name,
                            command=PoxController.pox_comand,
                            cargs=('--verbose ' if verbose else '') +
                            'openflow.of_01 --port=%d ' +
                            'dvni.' + script,
                            cdir=PoxController.pox_directory,
                            **kwargs)

    @staticmethod
    def copyScript(name):
        # type: (str) -> None
        """
        Copies the given script to POX's folder, used so POX can see the script.

        :param name: name of the script to be added to POX folder
        """

        copyToPath = PoxController.pox_directory + '/dvni'
        copyFromPath = os.path.dirname(__file__)
        filename = name + '.py'
        if not os.path.exists(copyToPath):
            os.makedirs(copyToPath)
        copyfile(copyFromPath + '/' + filename, copyToPath + '/' + filename)
