from ...models import Classroom, Student
import random


def generate_partnership_id(length):
    choices = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'M', 'P', 'Q', 'R', 'T', 'V', 'W', 'X', 'Y', '2', '3', '4', '6', '7',
               '8', '9']
    id = ''.join(random.choices(choices, k=length))
    while Student.objects.filter(partnership_id=id).exists():
        id = ''.join(random.choices(choices, k=length))
    return id


# takes in two class ids and creates partnerships based on student compatibility scores
def generate_partnerships(id1, id2):
    students1 = Student.objects.filter(class_id=id1)
    students2 = Student.objects.filter(class_id=id2)
    lone = any(not student.partnership_id for student in students1) or any(
        not student.partnership_id for student in students2)
    if not lone:
        return
    if (len(students1) > (len(students2) * 2)) or ((len(students1) * 2) < len(students2)):
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
            if p.username in available:  # username
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


def get_reset_email(username):
    teachers = Classroom.objects.filter(owner=username)
    if teachers:
        return teachers[0].email
    students = Student.objects.filter(username=username)
    if students:
        classroom = Classroom.objects.filter(class_id=students[0].class_id)
        return classroom[0].email
