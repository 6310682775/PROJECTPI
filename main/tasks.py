from celery.result import AsyncResult
from urllib import response
from django.contrib.auth import get_user_model
from celery import shared_task
import requests
import json


@shared_task
def detection(data):
    response = requests.post('http://127.0.0.1:5000/detect', json=data)
    # result = response.json()
    # process the result as needed
    # ...
    print(response)
    return "done"
