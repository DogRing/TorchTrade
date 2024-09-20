from kafka import KafkaConsumer
from ttrade import ttrade
import numpy as np
import json
import time
import os

topic=os.environ['TOPIC']
interval=int(60/int(os.environ.get('INTERVAL','15')))
data_count=int(os.environ.get('DATA_LENGTH','64'))*interval
kafka_host=os.environ.get('KAFKA_SERVICE','my-cluster-kafka-bootstrap.kafka.svc:9092')

consumer=KafkaConsumer(
    topic,
    bootstrap_servers=[kafka_host],
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=1000
)

try:
    x_data=np.zeros((6,data_count))
    data_index=np.where(np.arange(data_count) % 4 == 3)[0]
    while data_count > 0:
        for message in consumer:
            x_data=np.roll(x_data,-1,axis=1)
            x_data[0][-1]=message.value['timestamp']
            x_data[1][-1]=message.value['open']
            x_data[2][-1]=message.value['high']
            x_data[3][-1]=message.value['low']
            x_data[4][-1]=message.value['close']
            x_data[5][-1]=message.value['volume']
            data_count-=1
            if data_count == 0:
                break
    print(f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(message.value['timestamp']))}\ntick: {message.value['tick']}\noffset: {message.offset}\n")
    while True:
        for message in consumer:
            x_data=np.roll(x_data,-1,axis=1)
            x_data[0][-1]=message.value['timestamp']
            x_data[1][-1]=message.value['open']
            x_data[2][-1]=message.value['high']
            x_data[3][-1]=message.value['low']
            x_data[4][-1]=message.value['close']
            x_data[5][-1]=message.value['volume']
            ttrade(x_data[:,data_index])
finally:
    consumer.close()
