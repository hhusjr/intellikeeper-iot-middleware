from linkkit import linkkit
from time import sleep
import logging
import json
from handler import handler_mapping

LOG_FORMAT = '%(thread)d %(asctime)s  %(levelname)s %(filename)s %(lineno)d %(message)s'
DATE_FORMAT = '%m/%d/%Y-%H:%M:%S-%p'
logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT)

lk = linkkit.LinkKit(
    host_name='cn-shanghai',
    product_key='a1WC4bim5Ao',
    device_name='BASE-00000001',
    device_secret='rvTNFyFx2vKCuG1KAnZbfFt4GP4AMUZV')
lk.enable_logger(logging.DEBUG)


def on_topic_rrpc_message(id, topic, payload, qos, userdata):
    print('on_topic_rrpc_message: id:%s, topic:%s, payload:%s' % (id, topic, payload))
    request = json.loads(payload)
    action = request['action']
    lk.thing_answer_rrpc(id, json.dumps(handler_mapping[action](request)))


if __name__ == '__main__':
    print('Establishing connection...')
    lk.connect_async()
    sleep(5)

    lk.subscribe_rrpc_topic('request')
    lk.on_topic_rrpc_message = on_topic_rrpc_message

    print('Worker loop..')
    while True:
        pass
