ARG BUILD_FROM
FROM ${BUILD_FROM}

# Add env
ENV LANG C.UTF-8

ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

LABEL \
    io.hass.arch="${BUILD_ARCH}" \
    #io.hass.arch="armhf|armv7|aarch64|i386|amd64" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.vcs-ref=${BUILD_REF}

RUN apk add --no-cache curl
RUN apk add --no-cache python3

# install .py script dependency
RUN pip3 install requests
RUN pip3 install paho-mqtt
RUN pip3 install python-dotenv

# Copy data for add-on
# COPY ocr_aws.py /

COPY ocr_space.py /
COPY app.py /
COPY run.sh /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
