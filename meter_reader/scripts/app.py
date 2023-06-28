import paho.mqtt.client as mqtt
import requests
import os
import json
import time
import re
import pytesseract
from PIL import Image
import cv2

pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

CONFIG_PATH = "/data/options.json"

f = open(CONFIG_PATH)
config_json = json.loads(f.read())
f.close()

UPLOAD_FOLDER = './static/uploads'
FOLDER_PATH = config_json['folder_path']
IMAGE_TITLE = config_json['image_title']
# IMAGE_PATH = FOLDER_PATH + "/" + IMAGE_TITLE
IMAGE_PATH = os.path.join(FOLDER_PATH,IMAGE_TITLE)
today = time.strftime("%Y%m%d")
ksize = int(config_json['blur_ksize'])
inv = config_json['img_inverse']
rowS = int(config_json['crop_start_row'])
rowE = int(config_json['crop_end_row'])
colS = int(config_json['crop_start_col'])
colE = int(config_json['crop_end_col'])

# check/create log files
# =================================
mr_logs = open(f"{FOLDER_PATH}/mr_logs_{today}.txt", "a")
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

def classify(path_to_image, base_low, baseline, base_up, log):
    print("Calling model...")
    
    global ocrResult
    global reading
    global rowS
    global rowE
    global colS
    global colE
    global ksize
    global inv

    mr_logs = log
    ocrimgpath = IMAGE_PATH

    # preprocessing image
    # =================================
    # load the image
    img = cv2.imread(IMAGE_PATH)

    # crop image if values defined
    if (rowS|rowE|colS|colE) is not None:
        h, w, _ = img.shape
        if rowS is None :
            rowS = 0
        if rowE is None or rowE > h :
            rowE = h
        if rowS > rowE :
            rowS = 0
            print("Invalid crop setting. Reseted to image height.")
            mr_logs.write("Invalid crop setting. Reseted to image height.\n")
        if colS is None :
            colS = 0
        if colE is None or colE > w :
            colE = w
        if colS > colE : 
            colS = 0
            print("Invalid crop setting. Reseted to image width.")
            mr_logs.write("Invalid crop setting. Reseted to image widht.\n")
        img = img[rowS:rowE, colS:colE]

    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # apply median blurring to remove any blurring
    gray = cv2.medianBlur(gray, ksize)
    if (inv == True):
        gray = cv2.bitwise_not(gray)
    
    # save the processed image in the /static/uploads directory
    # ocrimgpath = os.path.join(UPLOAD_FOLDER,"{}.png".format(os.getpid()))
    ocrimgpath = os.path.join(FOLDER_PATH,"{}.png".format(os.getpid()))
    cv2.imwrite(ocrimgpath, gray)
    
    # model access can be replaced here
    # =================================
    ocrResult = pytesseract.image_to_string(Image.open(ocrimgpath))
    # =================================

    # # remove the processed image
    # os.remove(ocrimgpath)

    print("Model response received.")
    print(f"Response from TesseractOCR: {ocrResult}")
    mr_logs.write(f"Response from TesseractOCR: {ocrResult}\n")
    
    # postprocessing reading to remove everithing but numbers
    # =================================
    processed = re.sub(r"[^0-9]", "", ocrResult)[:8]
    print(f"Recognised digits: {processed}")
    mr_logs.write(f"Recognised digits: {processed}\n")

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
        error("Classification value is outside the acceptable (low-high) range.")
        print(base_low, value, base_up)
        mr_logs.write("Classification value is outside the acceptable (low-high) range.\n")
        mr_logs.write(f"Value: {value}\n")
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
    global ocrResult
          
    print("Starting loop")

    while True:
        
        starttime = time.time()
        today = time.strftime("%Y%m%d")
        mr_logs = open(f"{FOLDER_PATH}/mr_logs_{today}.txt", "a")
        mr_readings = open(f"{FOLDER_PATH}/mr_readings.txt", "a")

        print(time.ctime())        
        mr_logs.write(f"{time.ctime()}\n")
        mr_readings.write(f"{time.ctime()}")
        print('Classifying image...')
        reading = classify(IMAGE_PATH, base_low, baseline, base_up, mr_logs)
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
            mr_logs.write("MQTT Publish OK!\n")
        else:
            error("!!! Reading COMPROMISED! !!!")
            mr_logs.write("!!! Reading COMPROMISED! !!!\n")
            # mr_logs.write(f"Reading: {reading}\n")
            mr_readings.write(f"  Reading: {reading}\n")
            base_low = base_low - int(config_json["max_decrease"])
            base_up  = base_up + int(config_json["max_increase"])
            publish_low_high_mqtt(client, base_low, base_up)
            
        print("Closing MQTT connection...")
        client.disconnect()
        print("MQTT disconnected successfully.")
        mr_logs.write("MQTT disconnected successfully.\n")
        
        mr_logs.close()
        mr_readings.close()
        
        # shorten sleeping time with the elapsed loop time
        endtime = time.time()
        timedelta = endtime - starttime

        if (int(timedelta) < int(config_json["upd_interval"])):
            time.sleep(int(config_json["upd_interval"]) - int(timedelta))
        else:
            time.sleep(int(config_json["upd_interval"]))

if __name__ == '__main__':
    run()
