import paho.mqtt.client as mqtt
import requests
import json
import time
from ocr_space import ocr_space_file
import re

CONFIG_PATH = "/data/options.json"

f = open(CONFIG_PATH)
config_json = json.loads(f.read())
f.close()

FOLDER_PATH = config_json['folder_path']
IMAGE_TITLE = config_json['image_title']
IMAGE_PATH = FOLDER_PATH + "/" + IMAGE_TITLE

# check/create log files
# =================================
mr_logs = open(f"{FOLDER_PATH}/mr_logs.txt", "a")
mr_logs.close()
mr_readings = open(f"{FOLDER_PATH}/mr_readings.txt", "a")
mr_readings.close()
mr_lastread = open(f"{FOLDER_PATH}/mr_lastread.txt", "a")
mr_lastread.close()
# =================================

f = open(f"{FOLDER_PATH}/mr_lastread.txt")
lastread = f.read()
f.close()

# check/udate last reading in file
# =================================
lastvalue = int(0 if lastread == "" else lastread)
if (lastvalue >= int(config_json["initial"])):
    baseline = lastvalue
else :
    baseline = int(config_json["initial"])
    mr_lastread = open(f"{FOLDER_PATH}/mr_lastread.txt", "w")
    mr_lastread.write(f"{baseline}")
    mr_lastread.close()

base_low = baseline - int(config_json["max_decrease"])
base_up  = baseline + int(config_json["max_increase"])

prev = baseline
reading = ""

def error(msg):
    print(f"#### ERROR: {msg} ####")

def classify(path_to_image, base_low, baseline, base_up):
    print("Calling model...")
    
    global reading
    
    # model access can be replaced here
    # =================================
    response = ocr_space_file(filename=IMAGE_PATH, api_key=config_json['ocr_api_key'], ocr_engine=config_json['ocr_engine'])
    # =================================

    print("Model response received.")
    print(f"Response: {response}")

    # postprocessing reading to remove spaces/dots/commas
    # =================================
    print("Post-processing response...")
    parsedText = json.loads(response)['ParsedResults'][0]['ParsedText']
    processed = re.sub(r"( |,|\.)", "", parsedText)[:8]
    # processed = re.sub(r"( )", "", parsedText)[:8]
    
    print(f"Recognised digits: {processed}")

    # validate reading
    # =================================
    s = ""
    for digit in processed:
        try:
            int(digit)
            s += digit
        except ValueError:
            s += "0"

    # check if reading is inside the expected range
    # =================================
    value = int(0 if s == "" else s)
    if (base_low <= value and value <= base_up):
        prev = reading
        reading = s
        print(base_low, value, base_up)
    else:
        error("Reading classification value is outside the acceptable (low-high) range.")
        print(base_low, value, base_up)
        # reading = prev
        return ""

    print(f"Reading: {reading}")
    return reading

def reader(file):
    with open(file, "rb") as image_file:
        encoded_string = image_file.read()
        return encoded_string

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
    global baseline
    global base_low
    global base_up
    global prev
    global reading
    
    print("Starting loop")

    while True:
        
        mr_logs = open(f"{FOLDER_PATH}/mr_logs.txt", "w")
        mr_readings = open(f"{FOLDER_PATH}/mr_readings.txt", "a")
        
        print(time.ctime())
        mr_logs.write(f"{time.ctime()}\n")
        mr_readings.write(time.ctime())
        print('Classifying image...')
        reading = classify(IMAGE_PATH, base_low, baseline, base_up)
        print("Classification done.")
        mr_logs.write("Classification done.\n")

        print("Connecting to MQTT...")
        client = connect()
        print("MQTT connected successfully.")
        mr_logs.write("MQTT connected successfully.\n")

        if reading != "":
            print("✔️✔️✔️ Reading OK! ✔️✔️✔️")
            mr_logs.write("Reading OK!\n")
            baseline = int(reading)
            base_low = baseline - int(config_json["max_decrease"])
            base_up  = baseline + int(config_json["max_increase"])
            mr_logs.write(f"Reading: {reading}\n")
            mr_readings.write(f"  Reading: {reading}\n")
            mr_lastread = open(f"{FOLDER_PATH}/mr_lastread.txt", "w")
            mr_lastread.write(f"{reading}")
            mr_lastread.close()
            publish_mqtt(client, reading)
            publish_low_high_mqtt(client, base_low, base_up)
            mr_logs.write("MQTT Publish OK!")
        else:
            error("!!! Reading COMPROMISED! !!!")
            mr_logs.write("!!! Reading COMPROMISED! !!!")
            mr_readings.write(f"{reading}\n")
            base_low = base_low - int(config_json["max_decrease"])
            base_up  = base_up + int(config_json["max_increase"])
            publish_low_high_mqtt(client, base_low, base_up)
            
        print("Closing MQTT connection...")
        client.disconnect()
        print("MQTT disconnected successfully.")
        mr_logs.write("MQTT disconnected successfully.\n")
        
        mr_logs.close()
        mr_readings.close()
        

        time.sleep(int(config_json["upd_interval"]))

if __name__ == '__main__':
    run()
