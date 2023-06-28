# Meter Reader

OpenCV and Tesseract OCR based meter reader.

Put a webcam in front of your utility meter, OpenCV and Tesseract OCR classifies the image, and it sends the reading over MQTT server/broker of your choice.

## Usage

Use HA camera proxy integration to crop camera image, if needed.
https://www.home-assistant.io/integrations/proxy/

Create an automation to regularly take a snapshot of your camera image.

(Or use an ESP-CAM to take snapshots at regular intervals.)

Set up and start the addon.

Create an MQTT sensor in HA to subscribe to mqtt topic. 
https://www.home-assistant.io/integrations/sensor.mqtt/

## Configuration

### Reader

upd_interval: value in seconds to be used as interval between data refreshes

folder_path: where to find the snapshot of your meter camera image, and log will be saved

image_title: title of snapshot

initial: initial/current reading of your meter

max_increase: maximum expected increase during the reading period

max_decrease: maximum expected decrease during the reading period

### MQTT

mqtt_host, mqtt_port, mqtt_user, mqtt_pwd: find and get access to your MQTT server/broker

mqtt_topic: topic on which meter reading gets published

# Hint

Only the recognised numbers are transmitted, decimal places are set on the receiver side.