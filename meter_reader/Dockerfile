ARG BUILD_FROM
FROM ${BUILD_FROM}

# Add env
ENV LANG C.UTF-8

ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

LABEL \
    # io.hass.arch="${BUILD_ARCH}" \
    io.hass.arch="armhf|armv7|aarch64|i386|amd64" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.vcs-ref=${BUILD_REF}

# RUN apk add -X http://dl-cdn.alpinelinux.org/alpine/edge/testing/ -u alpine-keys --allow-untrusted
# RUN apk add -X http://dl-cdn.alpinelinux.org/alpine/edge/community -u alpine-keys --allow-untrusted
# RUN apk add -X http://dl-cdn.alpinelinux.org/alpine/edge/main -u alpine-keys --allow-untrusted
RUN apk add --allow-untrusted automake ca-certificates g++ git libtool libleptonica-dev make pkg-config 
RUN git clone https://github.com/tesseract-ocr/tesseract.git

RUN cd tesseract \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && ldconfig

RUN apk add --no-cache curl
RUN apk add --no-cache python3
RUN cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

# install .py script dependency
RUN pip3 install requests
RUN pip3 install paho-mqtt
RUN pip3 install python-dotenv
RUN pip3 install pytesseract

# Copy data for add-on
COPY ocr_space.py /
COPY app.py /
COPY run.sh /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]