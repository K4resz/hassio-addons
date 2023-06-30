# Meter Reader

OpenCV and Tesseract OCR based utility meter reader.

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

folder_path: folder path where the  temporary files and run logs will be saved

snapshot_path: image path where to find the snapshot from your meter camera

upd_interval: value in seconds to be used as interval between data refreshes

initial: initial/current reading of your meter

max_increase: maximum expected increase during the reading period

max_decrease: maximum expected decrease during the reading period

### OpenCV

crop_*: if defined image will be cropped 

ksize: it must be odd and greater than 1, for example: 3, 5, 7 ...

img_inverse: if true it will inverse image colors

### MQTT

mqtt_host, mqtt_port, mqtt_user, mqtt_pwd: find and get access to your MQTT server/broker

mqtt_topic: topic on which meter reading gets published

# Hint

Only the recognised numbers are transmitted, decimal places are set on the receiver side.