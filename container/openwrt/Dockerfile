FROM dvni/base as downloader
ENV OPENWRT_VERSION 17.01.4
ENV OPENWRT_NAME lede
#ENV OPENWRT_VERSION 18.06.2
#ENV OPENWRT_NAME openwrt
WORKDIR /tmp
RUN wget http://downloads.openwrt.org/releases/$OPENWRT_VERSION/targets/x86/generic/$OPENWRT_NAME-$OPENWRT_VERSION-x86-generic-generic-rootfs.tar.gz \
 && tar -xzf $OPENWRT_NAME-$OPENWRT_VERSION-x86-generic-generic-rootfs.tar.gz \
 && rm $OPENWRT_NAME-$OPENWRT_VERSION-x86-generic-generic-rootfs.tar.gz

LABEL maintainer="Keiran Young (kcyoung1997@hotmail.co.uk)"
FROM scratch
COPY --from=downloader /tmp /
# Symlink so that when Containernet calls bash sh is instead run
#RUN ln -s /bin/ash /bin/bash
RUN mkdir /var/lock && mkdir /var/run && opkg update && opkg install bash

EXPOSE 80

USER root
CMD ["/sbin/init"]
