from kazoo.client import KazooClient
from kazoo.recipe.election import Election
import time

# Zookeeper 서버 연결
zk = KazooClient(hosts='zk-cs.zookeeper.svc:2181')
zk.start()

# 리더 선출을 위한 경로 설정
election_path = "/ttrade/KRW-BTC"

def work_as_leader():
    print("I am the leader now. Performing leader tasks...")
    # 여기에 리더가 해야 할 작업을 정의하세요.
    while True:
        # 작업을 수행하는 부분
        time.sleep(5)
        print("Leader is doing work...")

def participate_in_election():
    election = Election(zk, election_path)
    
    # 리더 선출에 참여하고, 리더가 되었을 경우 작업 수행
    election.run(work_as_leader)

try:
    # 리더 선출에 참여
    print("Participating in leader election...")
    participate_in_election()
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    zk.stop()
    zk.close()