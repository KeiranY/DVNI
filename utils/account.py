"""
Host Account Management
=================================
"""
import random
from mininet.node import Docker


def add_user(host, username, password=None):
    # type: (Docker, str, str) -> None
    """Adds a user to a docker container, and sets it's password if given."""

    host.cmd("adduser --disabled-password --gecos \"\"", username)
    if password:
        change_password(host, username, password)


def change_password(host, username, password):
    # type: (Docker, str, str) -> None
    """Changes the password of a user on a docker container"""
    host.cmd("echo '%s:%s' | chpasswd" % (username, password))


def generate_password(length=20):
    # type: (int) -> str
    """Generates a password containing hexadecimal characters (0-9 & a-f)"""
    return ('%0'+str(length)+'x') % random.randrange(16 ** length)
