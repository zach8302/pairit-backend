import requests
from dateutil.relativedelta import *
import os
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")

def add_to_mailing_list(email, first):
    url = "https://app.loops.so/api/v1/contacts/create"
    body ={
        "email": email,
        "firstName": first,
        "userGroup": "Teachers",
        "source":"Sign up"
    }
    headers = {"Authorization": f"Bearer {LOOPS_API_KEY}"}

    return(requests.post(url, data=body, headers=headers))

def loops_event(email, event):
    url = "https://app.loops.so/api/v1/events/send"
    body = {
        "email": email,
        "eventName": event
    }
    headers = {"Authorization": f"Bearer {LOOPS_API_KEY}"}

    return(requests.post(url, data=body, headers=headers))

def loops_subscribe(email):
    url = "https://app.loops.so/api/v1/contacts/update"
    body = {
        "email": email,
        "userGroup": "Subscribers",
    }
    headers = {"Authorization": f"Bearer {LOOPS_API_KEY}"}

    return(requests.post(url, data=body, headers=headers))