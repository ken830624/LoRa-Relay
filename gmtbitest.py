import requests
import socket
import threading
import thread
import logging
import time
import paho.mqtt.client as mqtt
import json
import urllib2

GIOT_ULTopic_prefix = "GIOT-GW/UL/"
GIOT_DLTopic_prefix = "GIOT-GW/DL/"
LAN_MAC = "1C497B498D80"
LoRa_Wan_MAC = "00001c497b48db92"
Target_node_MAC = "000000000500005f"

mcs_data_format = {
    "datapoints": [
        {
            "dataChnId": "lora_temp",
            "values": {
                "value": "00.00"
            }
        },
        {
            "dataChnId": "lora_humi",
            "values": {
                "value": "00.00"
            }
        }
    ]
}

dl_test_counter = 0

downlink_data = [{"macAddr": "0000000005000023","data": "0023","id": "998877abcd0184", "extra": {"port": 2,"txpara": 6}}]

# change this to the values from MCS web console
DEVICE_INFO = {
    'device_id': 'D2vxFwNV',
    'device_key': 'd98BVa78SaYEj8MG'
}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(GIOT_ULTopic_prefix + LAN_MAC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
#    print(downlink_data)
    global dl_test_counter
#    downlink_data[0]['data'] = dl_test_counter
    json_extractor = json.loads(msg.payload)

    if json_extractor[0]['macAddr'] == Target_node_MAC:
        print("we published")
        downlink_data[0]['macAddr'] = Target_node_MAC
        downlink_data[0]['id'] = str(int(time.time()))
        client.publish(GIOT_DLTopic_prefix + LoRa_Wan_MAC, payload=json.dumps(downlink_data), qos=0, retain=False)

    dl_test_counter=dl_test_counter + 1
    # print(msg.topic+" "+str(msg.payload))
    json_extractor = json.loads(msg.payload)
    # print(json_extractor[0]['channel'])
    # print(json_extractor[0]['macAddr'])
    # print(json_extractor[0]['data'].decode("hex"))

    if json_extractor[0]['macAddr'] == Target_node_MAC:
        string_value = json_extractor[0]['data'].decode("hex")
        print("transmission_done")
        # print(string_value[1:6])
        # print(string_value[6:11])
        mcs_data_format['datapoints'][0]['values']['value'] = string_value[1:6]
        mcs_data_format['datapoints'][1]['values']['value'] = string_value[6:11]
        print(mcs_data_format)
        #req = urllib2.Request('http://api.mediatek.com/mcs/v2/devices/D2vxFwNV/datapoints')
        #req.add_header('deviceKey', 'd98BVa78SaYEj8MG')
        #req.add_header('Content-Type', 'application/json')

        #response = urllib2.urlopen(req, json.dumps(mcs_data_format))
        # print(response)

client = mqtt.Client(client_id="1C497B498D81", protocol=mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("lazyengineers", password="lazyengineers")
client.connect("104.199.215.165", port=1883, keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

if __name__ == '__main__':
    client.loop_forever()
