FROM dvni/base
LABEL maintainer="Keiran Young (kcyoung1997@hotmail.co.uk)"

RUN apt-get update && \
    apt-get install -y isc-dhcp-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN touch /var/lib/dhcp/dhcpd.leases

#VOLUME ["/var/lib/dhcp", "/etc/dhcp"]