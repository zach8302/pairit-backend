from todos_backend.settings import CALL_LENGTH
from ...models import Session, Student
import datetime
from dateutil.relativedelta import *
import os 
from opentok import OpenTok
LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
API_KEY = os.getenv("OPENTOK_API_KEY")
SECRET = os.getenv("OPENTOK_SECRET")
opentok = OpenTok(API_KEY, SECRET)
api_key = API_KEY

def create_session_data():
    session = opentok.create_session()
    session_id = session.session_id
    token = opentok.generate_token(session_id)
    return {'session_id' : session_id, 'token' : token}

# generates session keys and associates each one with a partnership
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