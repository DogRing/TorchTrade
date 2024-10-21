from data_transform import data_transform
from ttrade import ttrade
from kafka import KafkaConsumer
import pandas as pd
import numpy as np
import json
import time
import os

topic=os.environ['TOPIC']
tick=os.environ['TICK']
column_names=['timestamp','open','high','low','close','value']
interval=int(60/int(os.environ.get('INTERVAL','15')))
data_count=int(os.environ.get('DATA_LENGTH','200'))*interval
scaler_path = os.environ.get('SCALER_PATH','/data/data/scaler/')
kafka_host=os.environ.get('KAFKA_SERVICE','my-cluster-kafka-bootstrap.kafka.svc:9092')
tf_config_file=os.environ.get('DATA_CONFIG','/etc/config/transform.json')
config_file=os.environ.get('trade_config','/etc/config/trade.json')
with open(tf_config_file,'r') as f:
    tf_config=json.load(f)
with open(config_file,'r') as f:
    config=json.load(f)
input_count=int(os.environ.get('INPUT_LENGTH',config['seq_len']))

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
            df=data_transform(pd.DataFrame(x_data[data_index,:],columns=column_names),tf_config,path=scaler_path,file_name=tick,save=False)
            ttrade(df[config['features']][-input_count:].values.reshape(1,-1,len(config['features'])))
finally:
    consumer.close()
