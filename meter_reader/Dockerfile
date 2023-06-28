ARG BUILD_FROM
# FROM ${BUILD_FROM}
FROM alpine:latest

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

RUN apk update
RUN apk add --no-cache tesseract-ocr
RUN apk add --no-cache tesseract-ocr-data-eng
RUN apk add --no-cache curl 
RUN apk add --no-cache python3 
RUN apk add --no-cache py3-pip
RUN apk add --no-cache py3-numpy
RUN apk add --no-cache py3-opencv

# install .py script dependency
RUN pip3 install --upgrade pip
RUN pip3 install requests
RUN pip3 install paho-mqtt
RUN pip3 install python-dotenv
RUN pip3 install pytesseract


# Copy data for add-on
COPY ./scripts/* /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]