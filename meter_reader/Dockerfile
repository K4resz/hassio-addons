#ARG BUILD_FROM

FROM ubuntu:18.04
#FROM ${BUILD_FROM}

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository -y ppa:alex-p/tesseract-ocr
RUN apt-get update && apt-get install -y tesseract-ocr-all 

RUN mkdir /home/work
WORKDIR /home/work

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

RUN apt-get install python3 curl
#RUN apk add --no-cache curl
#RUN apk add --no-cache python3

# install .py script dependency
RUN pip3 install requests
RUN pip3 install paho-mqtt
RUN pip3 install python-dotenv
RUN pip3 install numpy opencv-contrib-python
RUN pip3 install pytesseract

WORKDIR /root/

# Copy data for add-on
COPY ocr_space.py /
COPY app.py /
COPY run.sh /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
