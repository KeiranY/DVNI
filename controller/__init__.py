import os

from mininet.clean import Cleanup, killprocs
from mininet.node import Controller
from shutil import copyfile


class PoxController(Controller):
    poxDir = "/var/pox"
    poxCmd = poxDir + '/pox.py'

    def __init__(self, name, script, verbose=False, **kwargs):

        PoxController.copyScript(script)
        Controller.__init__(self, name,
                            command=PoxController.poxDir + '/pox.py',
                            cargs=('--verbose ' if verbose else '') +
                            'openflow.of_01 --port=%d ' +
                            'dvni.' + script,
                            cdir=PoxController.poxDir,
                            **kwargs)

    @staticmethod
    def copyScript(name):
        """

        :param name: name of the script to be added to POX folder
        :return:
        """
        copyToPath = PoxController.poxDir + '/dvni'
        copyFromPath = os.path.dirname(__file__)
        filename = name + '.py'
        if not os.path.exists(copyToPath):
            os.makedirs(copyToPath)
        copyfile(copyFromPath + '/' + filename, copyToPath + '/' + filename)
