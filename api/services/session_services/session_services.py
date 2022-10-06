import os
from opentok import OpenTok

LOOPS_API_KEY = os.getenv("LOOPS_API_KEY")
API_KEY = os.getenv("OPENTOK_API_KEY")
SECRET = os.getenv("OPENTOK_SECRET")
opentok = OpenTok(API_KEY, SECRET)
api_key = API_KEY
CALL_LENGTH = 15


def create_session_data():
    session = opentok.create_session()
    session_id = session.session_id
    token = opentok.generate_token(session_id)
    return {'session_id': session_id, 'token': token}