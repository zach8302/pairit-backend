from .models import Classroom, Session, Student
import random
import string
import datetime
from opentok import OpenTok


API_KEY = "47406241"
SECRET = "d9be7bd185e27c4df1043efa3d8517614e24ca75"
opentok = OpenTok(API_KEY, SECRET)
api_key = API_KEY

def create_session_data():
    session = opentok.create_session()
    session_id = session.session_id
    token = opentok.generate_token(session_id)
    return {'session_id' : session_id, 'token' : token}

def generate_partnership_id(length):
    id = ''.join(random.choices(string.ascii_uppercase, k=length))
    while Student.objects.filter(partnership_id=id).exists():
        id = ''.join(random.choices(string.ascii_uppercase, k=length))
    return id

def generate_parnterships(id1, id2,):
    students1 = Student.objects.filter(class_id=id1)
    students2 = Student.objects.filter(class_id=id2)
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
                id = generate_partnership_id(6)
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