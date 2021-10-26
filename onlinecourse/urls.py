from django.urls import path
from . import views

app_name = 'onlinecourse'
urlpatterns = [

    path(route='', view=views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),

    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    path('submit/<int:pk>/', views.submit, name='submit'),
    path('result/<int:course_id>/<int:submission_id>/',
         views.show_exam_result, name='result'),

]
