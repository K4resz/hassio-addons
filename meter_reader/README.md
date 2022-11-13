# Meter Reader

Put a webcam in front of your utility meter, let OCR.space read, then send the reading over MQTT to a MQTT server/broker of your choice.

## Configuration

upd_interval: value in seconds to be used as interval between data refreshes.

image_path: where to find the picture of your meter (camera)

initial: initial/current reading of your meter

under: max you expect it to go down during an update interval (where I live solar panels allow meters to run backwards)

over: max you expect it to go up during an update interval

ocr.space token: see https://ocr.space/OCRAPI on how to get free API token

mqtt_host, mqtt_port, mqtt_user, mqtt_pwd: find and get access to your MQTT server

mqtt_topic: topic on which meter reading gets published

## Usage

Create an MQTT sensor in HA to subscribe to mqtt topic. 
https://www.home-assistant.io/integrations/sensor.mqtt/
