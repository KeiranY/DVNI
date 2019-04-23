DVNI
================================

Damn Vulnerable Network Infrastructure (DVNI) is a project based on Containernet that creates vulnerable Software Defined Networks (SDN) to allow users to practice Ethical Hacking techniques against Layer 2/3 network services.

Getting Started
=================
Requirements
-------------------

`Vagrant <https://www.vagrantup.com/downloads.html>`_ - The project runs within a virtual machine (VM), vagrant is used to download and configure this.

`VirtualBox <https://www.virtualbox.org/wiki/Downloads>`_ - The project is run inside a VirtualBox VM.

*FTP Client* - Task & answer sheets are provided over FTP.

*VNC Viewer OR a Web Browser* - Most tasks supply a Kali machine that is connected to through either VNC or NoVNC in a web browser.

Installation
-------------------

Once you have installed the required utilitiles start the project with Vagrant (First time setup may take some time):

``vagrant up``

After this has completed you are free to try out the scenarios!

You can connect to the project either using `VirtualBox` to view the VM or through SSH.

Connect to the device through SSH with the credentials `student`:`student` or `teacher`:`teacher` and follow the guidance from there:

``ssh student@10.10.0.1``
