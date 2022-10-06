from django.test import TestCase
from ...models import Student
from .class_services import generate_partnerships, generate_partnership_id
import random

def get_pers():
    val = 0
    for i in range(4):
        val *= 10
        val += random.randrange(1,5)
        
    return val

class PartnerTestCase(TestCase):
    def setUp(self):
        id1 = "hi"
        id2 = "bye"
        for _ in range(33):
            name1 = generate_partnership_id(10)
            name2 = generate_partnership_id(10)
            Student(first=name1, username=name1, personality=get_pers(), class_id=id1).save()
            Student(first=name2, username=name2, personality=get_pers(), class_id=id2).save()

    def test_equal_length(self):
        generate_partnerships("hi", "bye")
        qset1 = Student.objects.filter(class_id="hi")
        qset2 = Student.objects.filter(class_id="bye")
        self.assertTrue(all([s.partnership_id for s in qset1]))
        self.assertTrue(all([s.partnership_id for s in qset2]))
        
    def test_longer_length(self):
        qset = Student.objects.filter(class_id="bye")
        for i in range(3):
            qset[i].delete()
        generate_partnerships("hi", "bye")
        qset1 = Student.objects.filter(class_id="hi")
        qset2 = Student.objects.filter(class_id="bye")
        self.assertTrue(all([s.partnership_id for s in qset1]))
        self.assertTrue(all([s.partnership_id for s in qset2]))
        
    def test_shorter_length(self):
        qset = Student.objects.filter(class_id="hi")
        for i in range(3):
            qset[i].delete()
        generate_partnerships("hi", "bye")
        qset1 = Student.objects.filter(class_id="hi")
        qset2 = Student.objects.filter(class_id="bye")
        self.assertTrue(all([s.partnership_id for s in qset1]))
        self.assertTrue(all([s.partnership_id for s in qset2]))

# new_total = 0
# for s1 in c1:
#     partner = [s2 for s2 in c2 if s2.partner == s1.partner][0]
#     curr = comps[s1.name][partner.name]
#     new_total += curr