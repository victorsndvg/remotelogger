# -*- coding: utf-8 -*-

import logging
import pika
import socketio
from remotelogger.sio import sio
from gevent import monkey
monkey.patch_all()

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

class Consumer(object):

    def __init__(self, amqp_url, exchange, exchange_type, queue, routing_key, logger):
        self._connection = None
        self._channel = None
        self._closing = False
        self._timerid = None
        self._url = amqp_url
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._queue = queue
        self._routing_key = routing_key
        self.logger = logger

    def connect(self):
        self.logger.info('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        self.logger.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def add_on_connection_close_callback(self):
        self.logger.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
#        if self._closing:
#            self._connection.ioloop.stop()
#        else:
#            self.logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
#                           reply_code, reply_text)
#            self._connection.add_timeout(5, self.reconnect)
        self.stop()


    def reconnect(self):
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()
        if not self._closing:
            # Create a new connection
            self._connection = self.connect()
            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def open_channel(self):
        self.logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self.logger.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._exchange)

    def add_on_channel_close_callback(self):
        self.logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        self.logger.info('Channel %i was closed: (%s) %s', channel, reply_code, reply_text)
        self._connection.close()

    def setup_exchange(self, exchange_name):
        self.logger.info('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self._exchange_type)

    def on_exchange_declareok(self, unused_frame):
        self.logger.info('Exchange declared')
        self.setup_queue(self._queue)

    def setup_queue(self, queue_name):
        self.logger.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        self.logger.info('Binding %s to %s with %s', self._exchange, self._queue, self._routing_key)
        self._channel.queue_bind(self.on_bindok, self._queue,
                                 self._exchange, self._routing_key)

    def on_bindok(self, unused_frame):
        self.logger.info('Queue bound')
        self.start_consuming()

    def start_consuming(self):
        self.logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(consumer_callback=self.on_message,
                                                         queue=self._queue)

    def add_on_cancel_callback(self):
        self.logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        self.logger.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

#    async def show_message(self, uri, message):
#        async with websockets.connect(uri) as websocket:
#            await websocket.send(message)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        self.logger.info('Received message # %s from %s: %s', basic_deliver.delivery_tag, properties.app_id, body)
        self.acknowledge_message(basic_deliver.delivery_tag)
        sio.emit('my response', {'data': body.decode('utf-8')} , namespace='/test')


    def acknowledge_message(self, delivery_tag):
        self.logger.info('Acknowledging message %s', delivery_tag)
        #if self._timerid:
        #    self._closing = False
        #    self._connection.remove_timeout(self._timerid)
        self._channel.basic_ack(delivery_tag)
        #self._timerid = self._connection.add_timeout(60, self.close_channel)
        #self._closing = True

    def stop_consuming(self):
        if self._channel:
            self.logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def on_cancelok(self, unused_frame):
        self.logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def close_channel(self):
        self.logger.info('Closing the channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        self.logger.info('Stopping')
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.stop()
        #self._sio.disconnect(sid, namespace='/logs/logs')
        self.logger.info('Stopped')

    def close_connection(self):
        self.logger.info('Closing connection')
        self._connection.close()


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    ampq_url = 'amqp://guest:guest@broker:5672/%2F'
    exchange = 'exchange'
    exchange_type = 'direct'
    queue = 'queue'
    routing_key = 'routing_key'
    consumer_tag = 'logs'
    consumer = Consumer(ampq_url, exchange, exchange_type, queue, routing_key, logging)
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()


if __name__ == '__main__':
    main()