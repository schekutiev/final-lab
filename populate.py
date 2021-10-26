import os
import json
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
from django.db import connection
# Ensure settings are read
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

django.setup()

from onlinecourse.models import Course, Instructor, Learner, Lesson, Enrollment, Question, Choice, Submission
from django.contrib.auth import get_user_model
User = get_user_model()

def clean_data():
    # Delete all data to start from fresh
    Submission.objects.all().delete()
    Choice.objects.all().delete()
    Question.objects.all().delete()
    Enrollment.objects.all().delete()
    User.objects.all().delete()
    Learner.objects.all().delete()
    Instructor.objects.all().delete()
    Course.objects.all().delete()
    Lesson.objects.all().delete()
    print('Cleaned up!')


def populate_users():
    # Load Users
    filepath = os.getcwd() + '/json/users.json'
    with open(filepath, 'rt') as fh:
        users = json.load(fh)
    
    # Add User
    for user in users:
        user['username'] = (user['first_name'] + user['last_name']).lower()
        user['email'] = (user['first_name'] + '.' + user['last_name'] + '@gmail.com').lower()
        user['password'] = 'not_hashed'
        
        # creating Django object
        obj, created = User.objects.get_or_create(**user)

    print('User objects all saved... ')
    
    
def populate_instructors():
    filepath = os.getcwd() + '/json/instructors.json'
    # Load Instructors
    with open(filepath, 'rt') as fh:
        instructors = json.load(fh)
        
        # Add instructors
        for instructor in instructors:
            # get related user
            user = User.objects.get(last_name__icontains=instructor['last_name'])
            # creating Django object
            obj, created = Instructor.objects.get_or_create(
            # ignoring extra fields in JSON file
                user=user,
                full_time=bool(instructor['full_time']),
                total_learners=instructor['total_learners'],
            )

    print('Instructor objects all saved... ')


def populate_learners():
    # Load Learners
    filepath = os.getcwd() + '/json/learners.json'
    with open(filepath, 'rt') as fh:
        learners = json.load(fh)
    
    # Add learner
    for learner in learners:
        # get related user
        user = User.objects.get(last_name__icontains=learner['last_name'])
        # creating Django object
        obj, created = Learner.objects.get_or_create(
        # ignoring extra fields in JSON file
            user=user,
            occupation=learner['occupation'],
            social_link=learner['social_link'],
        )

    print('Learner objects all saved... ')

def populate_courses():
    filepath = os.getcwd() + '/json/courses.json'
    # Load Courses
    with open(filepath, 'rt') as fh:
        courses = json.load(fh)
        
        # Add Courses
        # Course.objects.bulk_create(courses)
        for course in courses:
            obj, created = Course.objects.get_or_create(**course)
            

    print('Course objects all saved... ')

def populate_lessons():
    filepath = os.getcwd() + '/json/lessons.json'
    # Load Lessons
    with open(filepath, 'rt') as fh:
        lessons = json.load(fh)

    # Add lessons
    for lesson in lessons:
        # get related course
        course = Course.objects.get(name__icontains=lesson['title'].split()[0])
        lesson['course'] = course
        # creating Django object
        obj, created = Lesson.objects.get_or_create(**lesson)

    print('Lesson objects all saved... ')
    
    
def populate_question():
    obj, created = Question.objects.get_or_create(text='What is Django?')
    obj, created = Question.objects.get_or_create(text='What is Django View?')
    obj, created = Question.objects.get_or_create(text='What is Django Model?')
    
    print("Question objects saved... ")
    
    
def populate_choice():
    obj, created = Choice.objects.get_or_create(text='A Web Framework', is_correct=True)
    obj, created = Choice.objects.get_or_create(text='A Movie', is_correct=False)
    obj, created = Choice.objects.get_or_create(text='The single, definitive source of information about your data', is_correct=True)
    obj, created = Choice.objects.get_or_create(text='Perform ORM for developers', is_correct=True)
    obj, created = Choice.objects.get_or_create(text='Class-Based View', is_correct=True)
    obj, created = Choice.objects.get_or_create(text='Function-Based View', is_correct=True)
    obj, created = Choice.objects.get_or_create(text='It is a Controller', is_correct=False)

    print("Choice objects saved... ")
    
            
def populate_course_instructor_relationships():
    # Get related instructors
    instructor_sever = Instructor.objects.get(user__last_name__icontains='sever')
    instructor_strik = Instructor.objects.get(user__last_name__icontains='strik')
    instructor_vorot = Instructor.objects.get(user__last_name__icontains='vorot')

    # Get related courses
    course_cloud = Course.objects.get(name__contains='Cloud')
    course_python = Course.objects.get(name__contains='Python')

    # Add instructors to courses
    course_cloud.instructors.add(instructor_sever)
    course_cloud.instructors.add(instructor_strik)
    course_python.instructors.add(instructor_vorot)
    
    print("Course-instructor relationships saved... ")


def populate_course_enrollment_relationships():

    # Get related courses
    course_cloud = Course.objects.get(name__contains='Cloud')
    course_python = Course.objects.get(name__contains='Python')

    # Get related learners
    learner_james = User.objects.get(first_name__icontains='James')
    learner_paige = User.objects.get(first_name__icontains='Paige')
    learner_dmitry = User.objects.get(first_name__icontains='Dmitry')
    learner_eric = User.objects.get(first_name__icontains='Eric')
    learner_peter = User.objects.get(first_name__icontains='Peter')

    # Add enrollments
    james_cloud = Enrollment.objects.create(user=learner_james, date_enrolled=datetime.date(2020, 8, 1),
                                            course=course_cloud, mode='audit')
    james_cloud.save()
    paige_cloud = Enrollment.objects.create(user=learner_paige, date_enrolled=datetime.date(2020, 8, 2),
                                         course=course_cloud, mode='honor')
    paige_cloud.save()
    dmitry_cloud = Enrollment.objects.create(user=learner_dmitry, date_enrolled=datetime.date(2020, 8, 5),
                                            course=course_cloud, mode='honor')
    dmitry_cloud.save()
    eric_cloud = Enrollment.objects.create(user=learner_eric, date_enrolled=datetime.date(2020, 8, 5),
                                           course=course_cloud, mode='audit')
    eric_cloud.save()
    peter_python = Enrollment.objects.create(user=learner_peter, date_enrolled=datetime.date(2020, 9, 2),
                                              course=course_python, mode='honor')
    peter_python.save()
    print("Course-learner relationships saved... ")
    
    
def populate_course_question_relationships():
    # Get related courses
    course_django = Course.objects.get(name__contains='Django')
    
    for object in Question.objects.all():
        if 'Django' in object.text:
            object.courses.add(course_django)
            
            
def populate_question_choice_relationships():
    # Get related questions
    django_main = Question.objects.get(text__contains='Django?')
    django_model = Question.objects.get(text__contains='Model')
    django_view = Question.objects.get(text__contains='View')
    
    # Get related choices
    framework = Choice.objects.get(text__icontains='framework')
    movie = Choice.objects.get(text__icontains='movie')
    data = Choice.objects.get(text__icontains='data')
    orm = Choice.objects.get(text__icontains='Perform')
    class_ = Choice.objects.get(text__icontains='class')
    function_ = Choice.objects.get(text__icontains='function')
    controller_ = Choice.objects.get(text__icontains='controller')
    
    # Add choices to questions
    # django_main.choice_set.add(framework)
    # django_model.choice_set.add(framework)
    
    movie.questions.add(django_main)
    framework.questions.add(django_main)
    framework.questions.add(django_model)
    data.questions.add(django_model)
    orm.questions.add(django_model)
    class_.questions.add(django_view)
    function_.questions.add(django_view)
    controller_.questions.add(django_view)
    

    
def main():
    """ """
    clean_data()
    populate_users()
    populate_instructors()
    populate_learners()
    populate_courses()
    populate_lessons()
    populate_question()
    populate_choice()
    populate_course_instructor_relationships()
    populate_course_enrollment_relationships()
    populate_course_question_relationships()
    populate_question_choice_relationships()


if __name__ == '__main__':
    main()