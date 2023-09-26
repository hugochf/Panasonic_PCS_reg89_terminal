import paho.mqtt.client as mqtt
import Crypto.Cipher.AES as AES
from datetime import datetime
import os
from random import randrange
import json


# MQTT info
server_ip = "34.96.156.219" # IIL SERVER
#server_ip = "52.156.56.170"  # ESI SERVER
meter_id = "J220006476" #default
topic_c2s = meter_id + "C2S"
topic_s2c = meter_id + "S2C"

# Define key
key = "000000" + meter_id
key = key.encode('utf-8')
mkey = key
hexkey = bytes.fromhex(key.hex())
hexmkey = bytes.fromhex(mkey.hex())
iv = "420#abA%,ZfE79@M".encode('utf-8')
hexiv = bytes.fromhex(iv.hex())

# Others
os.system('clear')
rec = []
mqtt_status = "Ready"

# MQTT connection - C2S
def on_connect(client, userdata, flags, rc):
    global mqtt_status
    global topic_c2s
    topic_c2s = meter_id + "C2S"
    key = "000000" + meter_id
    key = key.encode('utf-8')
    mkey = key
    hexkey = bytes.fromhex(key.hex())
    hexmkey = bytes.fromhex(mkey.hex())
    iv = "420#abA%,ZfE79@M".encode('utf-8')
    hexiv = bytes.fromhex(iv.hex())
    print("C2S Connected with result code "+str(rc))
    client.subscribe(topic_c2s)
    mqtt_status = "Connected to " + meter_id
# # MQTT connection - S2C
# def on_connect1(client1, userdata1, flags1, rc):
#     global mqtt_status
#     print("S2C Connected with result code "+str(rc))
#     client1.subscribe(topic_s2c)
#     mqtt_status = "Connected"

# Received message from - S2C
# def on_message1(client1, userdata1, msg1):
#     global hexkey, hexmkey
#     defaultkey = "69aF7&3KY0_kk89@"
#     defaultkey = defaultkey.encode('utf-8')
#     hexdefaultkey = bytes.fromhex(defaultkey.hex())
#     hexmsg = bytes.fromhex(msg1.payload.hex())
#     decipher =  AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
#     dec1 = decipher.decrypt(hexmsg)
#     # if (dec1[0:1].hex() == "7b"):
#     #     print(dec1.decode('utf-8'))
#     # else:
#     #     print('S2C Message...:', dec1.hex())

# Received message from - C2S
def on_message(client, userdata, msg):
    global hexkey, hexiv, hexmkey, rec, node, reg89, mqtt_status
    key = "000000" + meter_id
    key = key.encode('utf-8')
    mkey = key
    hexkey = bytes.fromhex(key.hex())
    hexmkey = bytes.fromhex(mkey.hex())
    iv = "420#abA%,ZfE79@M".encode('utf-8')
    hexiv = bytes.fromhex(iv.hex())
    
    if (msg.payload.hex() != "50"):
        key = "000000" + meter_id
        hexmsg = bytes.fromhex(msg.payload.hex())
        decipher =  AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
        dec = decipher.decrypt(hexmsg)
        #00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16
        #cc 00 4a 22 00 05 57 1f 00 07 01 03 02 05 80 ba b4 READ RESPONSE
        #cc 00 4a 22 00 05 57 1f 01 02 NO RESPONSE
        #2c 06 4a 22 00 05 21 1f 00 08 01 06 00 59 00 00 59 d9 SET ACK
        print(dec.hex())
        if ((dec[0:1].hex() == "2c") | (dec[0:1].hex() == "2d") | (dec[0:1].hex() == "cc")  | (dec[0:1].hex() == "cd")):
            if (dec[11:12].hex() == "03"):
                if (dec[12:13].hex() == "02"):
                    node = dec[10:11].hex()
                    reg89 = dec[13:15].hex()
                    reg89_binary= bin(int(reg89, 16))
                    mqtt_status = ("Node: " + node + "  " + "reg89: " + reg89_binary[2:])
            if (dec[11:12].hex() == "06"):
                if (dec[13:14].hex() == "59"):
                    node = dec[10:11].hex()
                    reg89 = dec[14:15].hex()
                    reg89_binary= bin(int(reg89, 16))
                    mqtt_status = ("Set Node " + node + " reg89 to " + reg89_binary[2:] + " Success")
            if (dec[8:10].hex() == "0102"):
                mqtt_status = ("Error: RS485 no response")
            if (dec[8:10].hex() == "0b08"):
                mqtt_status = ("Error: Busy")

        # Remove the tailing zero
        # num_nulls = 0
        # for i in range(len(dec)-1, -1, -1):
        #     if dec[i] == 0:
        #         num_nulls += 1
        #     else:
        #         break
        # try:
        #     rec = json.loads(dec[:-num_nulls].decode('utf-8'))
        # except Exception as e:
        #     rec = "Error"
        # if "properties" in rec:
        #     print(rec["properties"])

def connect_mqtt():
    global mqtt_status
    # 連線設定
    # 初始化地端程式
    client = mqtt.Client(meter_id[4:10]+str(randrange(999)))
    # client1 = mqtt.Client(meter_id[4:10]+str(randrange(999)))
    # 設定連線的動作
    client.on_connect = on_connect
    # client1.on_connect = on_connect1
    # 設定接收訊息的動作
    client.on_message = on_message
    # client1.on_message = on_message1
    # 設定登入帳號密碼
    # client.username_pw_set("try","xxxx")
    # 設定連線資訊(IP, Port, 連線時間)
    try:
        client.connect(server_ip, 1883, 600)
    except:
        print("Connect error...")
        mqtt_status = "Failed to connect..."
    # client1.connect(server_ip, 1883, 600)
    # 開始連線，執行設定的動作和處理重新連線問題
    # 也可以手動使用其他loop函式來進行連接
    client.loop_start()
    # client1.loop_start()

    # while True:
    #     time.sleep(1)   # 1秒待つ

def publish_mqtt(cmd):
        global topic_s2c, mqtt_status
        key = "000000" + meter_id
        key = key.encode('utf-8')
        mkey = key
        hexkey = bytes.fromhex(key.hex())
        hexmkey = bytes.fromhex(mkey.hex())
        iv = "420#abA%,ZfE79@M".encode('utf-8')
        hexiv = bytes.fromhex(iv.hex())
        payload = bytes.fromhex(cmd)
        decipher =  AES.new(key=hexkey, mode=AES.MODE_CBC, iv=hexiv)
        enc = decipher.encrypt(payload)
        print("Message...:" + enc.hex())
        #要發布的主題和內容
        client1 = mqtt.Client(meter_id[4:10]+str(randrange(999)))
        try:
            client1.connect(server_ip, 1883, 600)
        except:
            mqtt_status = "Failed to connect..."
        else:
            mqtt_status = "Command sent"
        topic_s2c = meter_id + "S2C"
        client1.publish(topic_s2c, enc)
        client1.disconnect()