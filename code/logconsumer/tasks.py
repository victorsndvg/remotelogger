from celery.decorators import task
from celery import shared_task
from celery.utils.log import get_task_logger
from celery_singleton import Singleton
from remotelogger.celery import app
from remotelogger.settings import BROKER_HOST, BROKER_URL
from logconsumer.consumer import Consumer
from logconsumer.server import RPCServer
from celery.signals import worker_ready
from celery.contrib.abortable import AbortableTask

logger = get_task_logger(__name__)

#@app.task(bind=True, ignore_result=True)
@worker_ready.connect
def init(sender=None, conf=None, **kwargs):
    response = serve.apply_async((), queue="celery", routing_key="celery")


@app.task(base=Singleton)
def serve():
    try:
        server = RPCServer(BROKER_URL, 'rpc_queue', '', logger)
        server.register_callback(consume)
        server.connect()
        server.consume()
    except Exception as e:
        raise e

@app.task(base=Singleton)
def consume(exchange, exchange_type, queue, routing_key):
    consumer = Consumer(exchange, exchange_type, queue, routing_key, logger)
    try:
        consumer.run()
    except:
        consumer.stop()



