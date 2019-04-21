FROM dvni/base

LABEL maintainer="Keiran Young <kcyoung1997@hotmail.co.uk>"

RUN apt-get update && \
    apt-get install -y vsftpd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/run/vsftpd/empty
