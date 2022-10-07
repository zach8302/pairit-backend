from ...services.loops_services.loops_services import loops_subscribe
from ...models import Classroom
import datetime
from dateutil.relativedelta import *
import os
import stripe

STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
stripe.api_key = STRIPE_API_KEY


def create_checkout_session(email):
    session = stripe.checkout.Session.create(
        success_url='http://app.talktodos.com/teacher?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://app.talktodos.com/teacher?canceled=true',
        customer_email=email,
        mode='subscription',
        allow_promotion_codes=True,
        # subscription_data={
        #     "trial_period_days": 30
        # },
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
            # FREAK OUT
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
            # FREAK OUT
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
