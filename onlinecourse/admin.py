from django.contrib import admin
from .models import Course, Instructor, Learner, Lesson, Enrollment, Question, Choice, Submission


class QuestionInline(admin.StackedInline):
    model = Question.courses.through
    extra = 2


# Register your models here.
class CourseAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class ChoiceInline(admin.TabularInline):
    model = Choice.questions.through
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'grade', 'created_at')
    list_filter = ['created_at']
    search_fields = ['text']


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'is_correct']


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Enrollment)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission)