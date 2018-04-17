#!/usr/bin/env python
import pika
import uuid

class RpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='broker'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def open(self, queue, exchange, exchange_type):
        self.channel.queue_declare(queue=queue)
        self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)

    def dispatch(self, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=message)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def send(self, message):
        print(" [x] Sent %r" % message)
        self.channel.basic_publish(exchange='logs', routing_key='logs', body="Message!")

    def close(self, queue, exchange):
        self.channel.exchange_delete(exchange=exchange, if_unused=False)
        self.channel.queue_delete(queue=queue, if_unused=False, if_empty=True)

rpc = RpcClient()

print(" [x] Requesting rpc(...)")
rpc.open('logs', 'logs', 'topic')
response = rpc.dispatch('{"action":"start", "queue":"logs"}')
print(" [.] Celery task: %s" % response)
for i in range(0,50):
    pass
    #rpc.send('Message!')
rpc.close('logs', 'logs')

