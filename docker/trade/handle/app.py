from data_transform import data_transform
from ttrade import ttrade
from kafka import KafkaConsumer
import pandas as pd
import numpy as np
import json
import time
import os

topic=os.environ['TOPIC']
column_names=['timestamp','open','high','low','close','value']
interval=int(60/int(os.environ.get('INTERVAL','15')))
data_count=int(os.environ.get('DATA_LENGTH','64'))*interval
kafka_host=os.environ.get('KAFKA_SERVICE','my-cluster-kafka-bootstrap.kafka.svc:9092')
config_file=os.environ.get('DATA_CONFIG','/etc/config/transform.json')
with open(config_file,'r') as f:
    config=json.load(f)

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
    num_features=len(column_names)
    x_data=np.zeros((data_count,num_features),dtype=np.float64)
    data_index=np.where(np.arange(data_count) % interval == (interval-1))[0]
    while data_count > 0:
        for message in consumer:
            x_data=np.roll(x_data,-1,axis=0)
            for i in range(num_features):
                x_data[-1][i]=message.value[column_names[i]]
            data_count-=1
    print(f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(message.value['timestamp']))}\ntick: {message.value['tick']}\noffset: {message.offset}\n")
    while True:
        for message in consumer:
            x_data=np.roll(x_data,-1,axis=0)
            for i in range(num_features):
                x_data[-1][i]=message.value[column_names[i]]
            df=data_transform(pd.DataFrame(x_data[data_index,:],columns=column_names),config,tick=topic,save=False)
            ttrade(df)
finally:
    consumer.close()
