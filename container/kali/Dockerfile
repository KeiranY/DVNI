FROM lukaszlach/kali-desktop:xfce-top10
LABEL base="https://github.com/lukaszlach/kali-desktop"
LABEL maintainer="Keiran Young (kcyoung1997@hotmail.co.uk)"

# Kali container doesn't run the usual cleanup utilities as we'll want to install tools
RUN apt-get update && \
    apt-get install -y net-tools iproute2 iputils-ping nmap psmisc
# DEV packages
RUN apt-get install -y arp-scan yersinia wireshark tcpdump
RUN apt-get install -y vlan


CMD /bin/bash
