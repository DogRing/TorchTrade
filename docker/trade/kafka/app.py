from kazoo.client import KazooClient
from kazoo.recipe.election import Election
from candle import candle_interval
import os

election_path="/ttrade/"+os.environ['TICK']
zookeeper_host=os.environ.get('ZK_SERVICE','zk-cs.zookeeper.svc:2181')
zk=KazooClient(hosts=zookeeper_host)

if __name__=="__main__":
    try:
        zk.start()
        election = Election(zk,election_path)
        print("Zookeeper Election")
        election.run(candle_interval)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        zk.stop()
        zk.close()
