#!/usr/bin/env python
import pika
import sys

def cancel():
    print("cancel ok")

connection = pika.BlockingConnection(pika.ConnectionParameters(host='broker'))
channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='topic')
message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='logs', body=message)
print(" [x] Sent %r" % message)
#channel.exchange_delete('logs')
#channel.basic_cancel(consumer_tag='logs')
#channel.close(reply_code=0, reply_text='Normal Shutdown!!!!!!!!!!!!!!!!!!!!')
channel.exchange_delete(exchange='logs', if_unused=False)
channel.queue_delete(queue='logs', if_unused=False, if_empty=False)
connection.close()
