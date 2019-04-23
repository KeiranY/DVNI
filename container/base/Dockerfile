FROM debian:stretch-slim
LABEL maintainer="Keiran Young (kcyoung1997@hotmail.co.uk)"

RUN apt-get update && \
    apt-get install -y wget net-tools iproute2 iputils-ping && \
    apt-get install -y procps netcat isc-dhcp-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD /bin/bash