from celery import Celery
from celery.schedules import crontab
import os
import redis
from dotenv import load_dotenv
from pathlib import Path
from time import time
from test import getVk, sendTg



env_path = Path.cwd() / '.env'
load_dotenv(env_path, override=True)

redis_string = f"redis://{os.getenv('REDIS_HOST')}/{os.getenv('REDIS_DB')}"

app = Celery(
    'tasks',
    backend=redis_string,
    broker=redis_string,
    )

redisAdapter = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    db=os.getenv('REDIS_DB'),
)

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'inspection.check',
        'schedule': crontab(minute='*/1'),
    },
}

app.conf.timezone = 'UTC'

@app.task
def check():
    currentTime = int(time())
    lastTime = redisAdapter.get('last_request_time') 
    if lastTime is None:
        redisAdapter.set('last_request_time', currentTime)
        return
    lastTime = int(lastTime)
    recentPosts = getVk(lastTime)
    redisAdapter.set('last_request_time', currentTime)
    return sendTg(recentPosts)
    