from .models import Classroom, Session, Student
import random
import string
import datetime
from dateutil.relativedelta import *
from opentok import OpenTok
import os
import stripe
import json
API_KEY = os.getenv("OPENTOK_API_KEY")
SECRET = os.getenv("OPENTOK_SECRET")
STRIPE_API_KEY = "sk_test_51LBPqlJCFUCx31oecgwiKdGrGJsQUzSkkyF4VDY6g8ub9kSkboDHMuqNSNSs1ipdj0Y8eGgkp1QebCywP7cGwaHZ00gDAxo4Go"
STRIPE_WEBHOOK_SECRET = "whsec_2c5895fba2a3034f2c0127df7713a35f3814ccbfbde8b59f15488d2403453534"
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

def generate_parnterships(id1, id2,):
    students1 = Student.objects.filter(class_id=id1)
    students2 = Student.objects.filter(class_id=id2)
    lone = any(not student.partnership_id for student in students1) or any(not student.partnership_id for student in students2)
    if not lone:
        return
    classes = [students1, students2]
    classes.sort(key=lambda x: len(x), reverse=True)
    long, short = classes
    avaiable = {s.username for s in short}
    
    for s1 in long:
        comps = [(s2, calculate_compatibility(s1, s2)) for s2 in short]
        comps.sort(key=lambda x: x[1], reverse=True)
        if not avaiable:
            for i in range(len(comps)):
                id = comps[i][0].partnership_id
                partners = Student.objects.filter(partnership_id=id)
                if len(partners) < 3:
                    s1.partnership_id = id
                    s1.save()  
                    break
            continue
        for p in comps:
            if p[0].username in avaiable:
                id = generate_partnership_id(8)
                s1.partnership_id = id
                p[0].partnership_id = id
                avaiable.remove(p[0].username)
                s1.save()
                p[0].save()
                break

def calculate_compatibility(student1, student2):
    score1 = student1.personality
    score2 = student2.personality
    compatibilty = 100
    while score1 and score2:
        compatibilty -= abs(score1 % 10 - score2 % 10)
        score1, score2 = score1 // 10, score2 // 10
    return compatibilty

def create_sessions(class_id, id):
    students = Student.objects.filter(class_id=class_id)
    seen = set()
    for s in students:
        partner = s.partnership_id
        if not partner in seen:
            data = create_session_data()
            session_id = data['session_id']
            token = data['token']
            expires=datetime.datetime.now() + datetime.timedelta(minutes=20)
            session = Session(partnership_id=partner, class_id=id, session_id=session_id, token=token, expires=expires)
            seen.add(partner)
            session.save()


def create_checkout_session(email):
    session = stripe.checkout.Session.create(
        success_url='http://localhost:3000/teacher?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:3000/teacher?canceled=true',
        customer_email=email,
        mode='subscription',
        line_items=[{
            'price': 'price_1LE0pHJCFUCx31oejbBER6ph',
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
    return customer.email == email

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
    return_url = 'http://localhost:3000'
    query = stripe.Customer.search(
        query=f"email:'{email}'",
    )
    customer_id = query.data[0].id
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url
    

