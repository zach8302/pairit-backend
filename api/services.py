from todos_backend.settings import CALL_LENGTH
from .models import Classroom, Session, Student
import random
import string
import datetime
import requests
from dateutil.relativedelta import *
from opentok import OpenTok
import os
import stripe
import json
API_KEY = os.getenv("OPENTOK_API_KEY")
SECRET = os.getenv("OPENTOK_SECRET")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
opentok = OpenTok(API_KEY, SECRET)
api_key = API_KEY
stripe.api_key = STRIPE_API_KEY


def create_session_data():
    session = opentok.create_session()
    session_id = session.session_id
    token = opentok.generate_token(session_id)
    return {'session_id' : session_id, 'token' : token}

def generate_partnership_id(length):
    choices = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'M', 'P', 'Q', 'R', 'T', 'V', 'W', 'X', 'Y', '2', '3', '4', '6', '7', '8', '9']
    id = ''.join(random.choices(choices, k=length))
    while Student.objects.filter(partnership_id=id).exists():
        id = ''.join(random.choices(choices, k=length))
    return id
    
def generate_partnerships(id1, id2):
    students1 = Student.objects.filter(class_id=id1)
    students2 = Student.objects.filter(class_id=id2)
    lone = any(not student.partnership_id for student in students1) or any(not student.partnership_id for student in students2)
    if not lone:
        return
    classes = [students1, students2]
    classes.sort(key=lambda x: len(x), reverse=True)
    long, short = classes
    comps = find_compatibilities(long, short)
    old_total = first_choice(long, short, comps)
    reverse = long[:]
    reverse.reverse()
    partner_swaps(reverse, short, comps)
    new_total = 0
    for s1 in long:
        partner = [s2 for s2 in short if s2.partnership_id == s1.partnership_id][0]
        curr = comps[s1.username][partner.username]
        new_total += curr
    print(old_total, new_total)

def find_compatibilities(long, short):
    comps = {}
    for s1 in long:
        individual = {}
        for s2 in short:
            individual[s2.username] = calculate_compatibility(s1, s2)
        comps[s1.username] = individual
    
    return comps

def calculate_compatibility(student1, student2):
    score1 = student1.personality
    score2 = student2.personality
    compatibilty = 0
    while score1 and score2:
        if score1 % 10 == score2 % 10:
            compatibilty += 1
        score1, score2 = score1 // 10, score2 // 10
    return compatibilty

def first_choice(long, short, comps):
    available = set([s.username for s in short])
    old_total = 0
    for s1 in long:
        indiv = comps[s1.username]
        students = short[:]
        students.sort(key=lambda x: indiv[x.username], reverse=True)

        if not available:
            for p in students:
                id = p.partnership_id
                partners = [s2 for s2 in short if s2.partnership_id == id]
                if len(partners) < 2:
                    s1.partnership_id = id
                    s1.save()
                    break
            continue
        for p in students:
            if p.username in available: # username
                old_total += indiv[p.username]
                id = generate_partnership_id(7)
                s1.partnership_id = id
                p.partnership_id = id
                s1.save()
                p.save()
                available.remove(p.username)
                break
    return old_total

def partner_swaps(long, short, comps):
    more = True
    while more:
        more = any([find_swap(s, long, short, comps) for s in long])

def find_swap(s1, long, short, comps):
    partner = [s2 for s2 in short if s2.partnership_id == s1.partnership_id][0]
    curr = comps[s1.username][partner.username]
    options = []
    for other in long:
        other_partner = [s2 for s2 in short if s2.partnership_id == other.partnership_id][0]
        other_curr = comps[other.username][other_partner.username]
        current = curr * other_curr
        new1 = comps[s1.username][other_partner.username]
        new2 = comps[other.username][partner.username]
        new = new1 * new2
        options.append(new - current)
    best = max(options)
    if best > 0:
        ind = options.index(best)
        temp = s1.partnership_id
        other = long[ind]
        s1.partner = other.partnership_id
        other.partnership_id = temp
        s1.save()
        other.save()
        return True
    else:
        return False

def create_sessions(class_id, id):
    students = Student.objects.filter(class_id=class_id)
    seen = set()
    for s in students:
        partner = s.partnership_id
        if not partner in seen:
            data = create_session_data()
            session_id = data['session_id']
            token = data['token']
            expires=datetime.datetime.now() + datetime.timedelta(minutes=CALL_LENGTH)
            session = Session(partnership_id=partner, class_id=id, session_id=session_id, token=token, expires=expires)
            seen.add(partner)
            session.save()


def create_checkout_session(email):
    session = stripe.checkout.Session.create(
        success_url='http://app.talktodos.com/teacher?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://app.talktodos.com/teacher?canceled=true',
        customer_email=email,
        mode='subscription',
        allow_promotion_codes = True,
        subscription_data= {
            "trial_period_days": 30
        },
        line_items=[{
            'price': 'price_1LQKNXJCFUCx31oeMfr5Wxp4',
            # For metered billing, do not pass quantity
            'quantity': 1,
            
        }],
    )
    if session and "url" in session:
        return session.url
    return None

def webhook_received(request):
    webhook_secret = STRIPE_WEBHOOK_SECRET
    request_data = request.body.decode('utf-8')

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request_data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            print(e)
            return False
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'checkout.session.completed':
        email = data.object.customer_details.email
        queryset = Classroom.objects.filter(email=email)
        if not queryset:
            #FREAK OUT
            return False
        classroom = queryset[0]
        classroom.expires = datetime.datetime.now() + relativedelta(months=+1)
        classroom.save()

    elif event_type == 'invoice.paid':
    # Continue to provision the subscription as payments continue to be made.
    # Store the status in your database and check when a user accesses your service.
    # This approach helps you avoid hitting rate limits.
        email = data.object.customer_email
        queryset = Classroom.objects.filter(email=email)
        if not queryset:
            #FREAK OUT
            return False
        classroom = queryset[0]
        classroom.expires = datetime.datetime.now() + relativedelta(months=+1)
        classroom.save()

    elif event_type == 'invoice.payment_failed':
    # Handle payment failure
        print(data)
    else:
        print('Unhandled event type {}'.format(event_type))
        return False

    return True

def validate_session(id, email):
    session = stripe.checkout.Session.retrieve(id)
    customer = stripe.Customer.retrieve(session.customer)
    if customer.email == email:
        loops_subscribe(email)
        return True
    return False
    

def check_sub(email):
    customer = stripe.Customer.search(
        query=f'email:"{email}"',
        expand=['data.subscriptions']
    )
    if not customer:
        return False
    print(dir(customer))
    subs = customer.data[0].subscriptions.data
    for sub in subs:
        if sub.status == "active" or sub.status == "trialing":
            return True
    return False


def create_portal(email):
    return_url = 'https://app.talktodos.com'
    query = stripe.Customer.search(
        query=f"email:'{email}'",
    )
    customer_id = query.data[0].id
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url

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
    
def get_reset_email(username):
    teachers = Classroom.objects.filter(owner=username)
    if teachers:
        return teachers[0].email
    students = Student.objects.filter(username=username)
    if students:
        classroom = Classroom.objects.filter(class_id=students[0].class_id)
        return classroom[0].email

