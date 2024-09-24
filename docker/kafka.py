

from kafka import KafkaProducer
producer = KafkaProducer(
    acks=0,                                                             # 전송 완료 체크
    compression_type='gzip',                                            # 메시지 전달 시 압축 
    bootstrap_servers=['my-cluster-kafka-bootstrap.kafka.svc:9092'],    # 브로커 주소
    value_serializer=lambda x: json.dumps(x).encode('utf-8')                 # 메시지의 값 직렬화
)

from kafka import KafkaConsumer
consumer = KafkaConsumer(
    'mytopic1',                                                         # 토픽명
    bootstrap_servers=['my-cluster-kafka-bootstrap.kafka.svc:9092'],    # 브로커 주소
    auto_offset_reset='earliest',                                       # 오프셋 위치 (earliest 처음, latest: 최근)
    enable_auto_commit=True,                                            # 오프셋 자동 커밋 여부
    group_id='my-group',                                                # 컨슈머 그룹 식별자
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),         # 메시지 역직렬화 
    consumer_timeout_ms=1000                                            # 데이터를 기기다리는 최대 시간
)
for message in consumer:
    print(f'Topic : {message.topic}, Partition : {message.partition}, Offset : {message.offset}, Key : {message.key}, value : {message.value}')

