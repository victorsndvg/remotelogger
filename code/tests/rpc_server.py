#!/usr/bin/env python
import pika


class FibonacciRpcServer(object):

    def __init__(self, host, queue, exchange):
        self.host       = host
        self.queue      = queue
        self.exchange   = exchange
        self.connection = None
        self.channel    = None

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel    = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def fib(self, n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return self.fib(n-1) + self.fib(n-2)

    def on_request(self, ch, method, props, body):
        n = int(body)

        print(" [.] fib(%s)" % n)
        response = self.fib(n)

        ch.basic_publish(   exchange=self.exchange, 
                            routing_key=props.reply_to,
                            properties=pika.BasicProperties(correlation_id=props.correlation_id),
                            body=str(response)
                        )
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.queue)
        print(" [x] Awaiting RPC requests")
        self.channel.start_consuming()

server = FibonacciRpcServer('broker', 'rpc_queue', '')
server.connect()
server.consume()
