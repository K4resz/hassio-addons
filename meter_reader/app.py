import paho.mqtt.client as mqtt
import requests
import json
import time
from ocr_space import ocr_space_file
import re

#IMAGE_PATH = "/config/www/meter.jpg"
CONFIG_PATH = "/data/options.json"

config_json = json.loads(open(CONFIG_PATH).read())

IMAGE_PATH = config_json['image_path']
baseline = int(config_json["baseline"])
base_low = baseline - int(config_json["under"])
base_up  = baseline + int(config_json["over"])

prev = baseline
reading = ""

def error(msg):
    print(f"#### ERROR: {msg} ####")

def classify(path_to_image, base_low, baseline, base_up):
    print("Calling model...")

    # model access can be replaced here
    # =================================
    response = ocr_space_file(filename=IMAGE_PATH, api_key=config_json['ocr_api_key'])
    # =================================

    print("Model response received.")
    print(f"Response: {response}")

    print("Post-processing response...")
    parsedText = json.loads(response)['ParsedResults'][0]['ParsedText']
    processed = re.sub(r"( |,|\.)", "", parsedText)[:8]

    print(f"Recognised digits: {processed}")

    s = ""
    for digit in processed:
        try:
            int(digit)
            s += digit
        except ValueError:
            s += "0"

    value = int(s)
    if (base_low <= value and value <= base_up):
        prev = reading
        reading = s
        print(base_low, value, base_up)
    else:
        error("Reading classification value is outside the acceptible (low-high) range.")
        # reading = prev
        return ""

    print(f"Reading: {reading}")
    return reading

def reader(file):
    with open(file, "rb") as image_file:
        encoded_string = image_file.read()
        return encoded_string

def take_photo(path):
    """
    Accesses image data from IP camera, and downloads the binary data to a file into the location specified in `path`
    """
    # download the url contents in binary format
    r = requests.get(config_json["url"])
    # r = requests.get(config_json["url"], auth=(config_json["user"], config_json["password"]))
    # open method to open a file on your system and write the contents
    with open(path, "wb") as code:
        code.write(r.content)
    print("File downloaded")

def connect():
    client = mqtt.Client("meter_reader")
    client.username_pw_set(username=config_json["mqtt_user"], password=config_json["mqtt_pwd"])
    client.connect(config_json["mqtt_host"], int(config_json["mqtt_port"]))
    return client

def disconnect(client):
    client.diconnect()

def publish_mqtt(client, reading):
    client.publish(config_json["mqtt_topic"], reading)

def publish_low_high_mqtt(client, low, high):
    print("Sending low and high data range...")
    client.publish("home/band/low", str(low))
    client.publish("home/band/high", str(high))

def run():
    while True:
        # print("Starting image gathering process...")
        # take_photo(IMAGE_PATH)
        # print("Photo downloaded.")

        print('Classifying image...')
        reading = classify(IMAGE_PATH, baseline, base_low, base_up)
        print("Classification done.")

        print("Connecting to MQTT...")
        client = connect()
        print("MQTT connected successfully.")

        if reading != "":
            print("✔️✔️✔️ Reading OK! ✔️✔️✔️")
            baseline = int(reading)
            base_low = baseline - int(config_json["under"])
            base_up  = baseline + int(config_json["over"])
            publish_mqtt(client, reading)
            publish_low_high_mqtt(client, base_low, base_up)
        else:
            error("Reading COMPROMISED!")
            base_low = base_low - int(config_json["under"])
            base_up  = base_up + int(config_json["over"])
            publish_low_high_mqtt(client, base_low, base_up)

        print("Closing MQTT connection...")
        client.disconnect()
        print("MQTT disconnected successfully.")

        time.sleep(int(config_json["upd_interval"]))

if __name__ == '__main__':
    run()
