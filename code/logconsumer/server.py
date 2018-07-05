#!/usr/bin/env python
from celery.task.control import revoke
import pika
import json

class RPCServer(object):

    def __init__(self, url, queue, exchange, logger):
        self.url        = url
        self.queue      = queue
        self.exchange   = exchange
        self.logger     = logger
        self.connection = None
        self.channel    = None
        self.callbacks  = []
        self.logger.info("RPC Server: Created")

    def connect(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(self.url))
        self.channel    = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)
        self.logger.info("RPC Server: Connected")

    def register_callback(self, callback):
        self.callbacks.append(callback)
        self.logger.info("RPC Server: Callback registered (%s)" % callback.__name__)

    def check_arguments(self, arguments):
        if arguments == None or not 'action' in arguments:
            self.logger.info("RPC Server: Invalid arguments (%s)" % arguments)
            return

        if arguments['action'] == 'start' and not 'queue' in arguments:
            self.logger.info("RPC Server: Start requires 'queue' (%s)" % arguments)

    def on_request(self, ch, method, props, body):
        response = None

        args = json.loads(body.decode('utf-8'))

        for callback in self.callbacks:
            self.logger.info("RPC Server: Start consuming (%s)" % args['queue'])
            response = callback.apply_async((args['exchange'],args['exchange_type'],args['queue'],args['routing_key'],), queue="consumer", routing_key="consumer")

        ch.basic_publish(   exchange=self.exchange, 
                            routing_key=props.reply_to,
                            properties=pika.BasicProperties(correlation_id=props.correlation_id),
                            body=str(response)
                        )
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.queue)
        self.logger.info("RPC Server: Awaiting RPC requests")
        self.channel.start_consuming()

if __name__ == "__main__":
    server = RPCServer('broker', 'rpc_queue', '')
    server.register_callback(consume)
    server.connect()
    server.consume()


