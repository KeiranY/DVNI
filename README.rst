DVNI
====

Damn Vulnerable Network Infrastructure (DVNI) is a project based on Containernet that creates vulnerable Software Defined Networks (SDN) to allow users to practice Ethical Hacking techniques against Layer 2/3 network services.

Getting Started
===============
Requirements
---------------

`Vagrant <https://www.vagrantup.com/downloads.html>`_ - The project uses a virtual machine (VM) which is downloaded and configured using vagrant.

`VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_ - used to run the VM.

*FTP Client* - Task & answer sheets are provided over FTP.

*VNC Viewer OR a Web Browser* - Most tasks supply a Kali machine that is connected to through either VNC or NoVNC in a web browser.

Installation
------------

Once you have installed the required utilitiles simply start the project with Vagrant (First time setup may take some time):

``vagrant up``

After this has completed you are free to try out the scenarios!

Usage
-----

You can connect to the project either using `VirtualBox` to view the VM or through SSH.

Connect to the device through SSH with the credentials `student`:`student` or `teacher`:`teacher` and follow the guidance from there:

``ssh student@10.10.0.1``

Development
-----------

To access the VM without being connected directly to the project, connect with Vagrant:

``vagrant ssh``

To run DVNI as a developer run `start.py` from the project root.

``python /vagrant/start.py``

You can also run scenarios and containers directly, although these options are available through `start.py`:

``python /vagrant/scenarios/HostScanning.py``
``python /vagrant/containers/``

Documentation
-------------
Documentation is available online provided by `GitHub.io <https://kcyoung1997.github.io/DVNI-docs/>`_.

The documentation is created with `Sphinx <http://www.sphinx-doc.org/>`_ and `ReadTheDocs <http://www.sphinx-doc.org/>`_.
To generate the documentation run the makefile in the `docs` folder:

``make html``


