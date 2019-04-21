FROM dvni/base

LABEL maintainer="Keiran Young <kcyoung1997@hotmail.co.uk>"

RUN apt-get update && \
    apt-get install -y pure-ftpd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
