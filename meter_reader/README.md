# Meter Reader

Put a webcam in front of your utility meter, let OCR.space read, then send the reading over MQTT server/broker of your choice.

## Usage

Use HA camera proxy integration to crop camera image, if needed.
https://www.home-assistant.io/integrations/proxy/

Create an automation to regularly take a snapshot of your camera image.

Get a free API Token from https://ocr.space/OCRAPI

Set up and start the addon.

Create an MQTT sensor in HA to subscribe to mqtt topic. 
https://www.home-assistant.io/integrations/sensor.mqtt/

## Configuration

### Reader

upd_interval: value in seconds to be used as interval between data refreshes.

image_path: where to find the snapshot of your meter camera image

initial: initial/current reading of your meter

max_increase: maximum expected increase during the reading period

max_decrease: maximum expected decrease during the reading period

### OCR

ocr_api_key: see https://ocr.space/OCRAPI on how to get free API token

ocr_engine: see https://ocr.space/OCRAPI for available engines, default is OCR Engine5

### MQTT

mqtt_host, mqtt_port, mqtt_user, mqtt_pwd: find and get access to your MQTT server/broker

mqtt_topic: topic on which meter reading gets published