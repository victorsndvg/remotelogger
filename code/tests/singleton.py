from celery.decorators import task
from django.core.cache import cache
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


class SingletonTask(task):
    def __call__(self, *args, **kwargs):
        lock = cache.lock(self.name)

        if not lock.acquire(blocking=False):
            logger.info("{} failed to lock".format(self.name))
            return

        try:
            super().__call__(*args, **kwargs)
        except Exception as e:
            lock.release()
            raise e
        lock.release()

def __call__(*args, **kwargs):
    lock = cache.lock('name')

    if not lock.acquire(blocking=False):
        logger.info("{} failed to lock".format('name'))
        return

    try:
        super().__call__(*args, **kwargs)
    except Exception as e:
        lock.release()
        raise e
    lock.release()
