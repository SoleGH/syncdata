# coding:utf-8

from celery import Celery

app = Celery('celery_main',broker='redis://localhost')

@app.task
def publish(arg1,arg2):
    return arg1 + arg2
