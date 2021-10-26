from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    """ User registration """
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name, 
                last_name=last_name,
                password=password,
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    """ User log in """
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    """ User log out """
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    """ Checks weather user is enrolled in a course """
    if user.id is not None:
        user_enrollment_count = Enrollment.objects.filter(
            user=user, course=course).count()
        if user_enrollment_count:
            return True
    return False

    # v2
    # is_enrolled = False
    # if user.id is not None:
    #     user_enrollment_count = Enrollment.objects.filter(
    #         user=user, course=course).count()
    #     is_enrolled = bool(user_enrollment_count)
    # return is_enrolled

    # v1 (original version)
    # is_enrolled = False
    # if user.id is not None:
    #     # Check if user enrolled
    #     num_results = Enrollment.objects.filter(
    #         user=user, course=course).count()
    #     if num_results > 0:
    #         is_enrolled = True
    # return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    """ Returns list of all courses template. No paginition. Sorry) """
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    """ Returns course detail template and 'is_enrolled' template condition """
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'

    # add is_enrolled in detail view context dictionary
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_obj = self.get_object()
        user = self.request.user
        is_enrolled = check_if_enrolled(user, course_obj)
        context.update({
            'is_enrolled': is_enrolled,
        })
        return context


def enroll(request, course_id):
    """ Returns course detail template if enrolled. Enrolls user if not enrolled yet """
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create a submit view to create an exam submission record for a course enrollment,
# you may implement it based on following logic:
         # Get user and course object, then get the associated enrollment object created when the user enrolled the course
         # Create a submission object referring to the enrollment
         # Collect the selected choices from exam form
         # Add each selected choice object to the submission object
         # Redirect to show_exam_result with the submission id
def submit(request, pk):
    """ Returns exam result template if submitted and detail template if not """
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=pk)
        user = request.user

        # getting m2m-related objects
        enrollment_object = get_object_or_404(
            Enrollment, user=user, course=course)
        submission_object = Submission.objects.create(
            enrollment=enrollment_object)

        # getting answers(choices) ids
        submitted_anwsers = [
            int(request.POST[key])
            for key in request.POST
            if key.startswith('choice')
        ]

        # getting choice objects list by ids
        choice_object_list = []
        for id in submitted_anwsers:
            choice_object = get_object_or_404(Choice, id=id)
            choice_object_list.append(choice_object)
        print(choice_object_list)

        submission_object.choices.add(*choice_object_list)
        # for choice_obj in choice_object_list:
        #     submission_object.choices.add(choice_obj)

        return HttpResponseRedirect(reverse(viewname='onlinecourse:result', args=(pk, submission_object.pk)))
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(pk,)))


# <HINT> A example method to collect the selected choices from the exam form from the request object
# def extract_answers(request):
#     submitted_anwsers = []
#     for key in request.POST:
#         if key.startswith('choice'):
#             value = request.POST[key]
#             choice_id = int(value)
#             submitted_anwsers.append(choice_id)
    # [int(request.POST[key]) for key in request.POST if key.startswith('choice')]
    # return submitted_anwsers


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score
def show_exam_result(request, course_id, submission_id):
    """ Returns exam result template  """
    course_obj = get_object_or_404(Course, pk=course_id)
    submission_obj = get_object_or_404(Submission, pk=submission_id)
    submission_choices = submission_obj.choices.all()
    choice_ids = [choice_obj.id for choice_obj in submission_choices]

    max_score, question_score = 0, 0

    course_questions = course_obj.question_set.all()
    for question in course_questions:
        max_score += question.grade
        if question.is_get_score(choice_ids):
            question_score += question.grade

    context = {
        "course": course_obj,
        "choices": submission_choices,
        "grade": int(question_score / max_score * 100),
    }

    print(question_score, max_score)
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)



