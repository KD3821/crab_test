from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import *
from django.urls import reverse, path
from django.utils.http import urlencode
from django.utils.html import format_html



@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'view_tests_link']

    def view_tests_link(self, obj):
        count = obj.quiz_set.count()
        url = (
                reverse("admin:quiz_quiz_changelist")
                + "?"
                + urlencode({"topic__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Кол-во тестов: {} </a>', url, count)

    view_tests_link.short_description = "Тесты"


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic', 'view_questions_link']
    list_filter = ['topic']

    def view_questions_link(self, obj):
        count = obj.question_set.count()
        url = (
                reverse("admin:quiz_question_changelist")
                + "?"
                + urlencode({"quiz__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">кол-во вопросов: {} </a>', url, count)

    view_questions_link.short_description = "Вопросы"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'view_answers_link']
    list_filter = ['topic_name', 'quiz']
    exclude = ['topic_name']

    def view_answers_link(self, obj):
        count = obj.option_set.count()
        url = (
                reverse("admin:quiz_option_changelist")
                + "?"
                + urlencode({"question__id": f"{obj.id}"})
        )
        return format_html('<a href="{}"> Кол-во ответов: {} </a>', url, count)

    view_answers_link.short_description = "Ответы"


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    change_list_template = 'admin/options_change_list.html'

    list_display = ['answer_text', 'question', 'is_correct', 'question_id', 'topic_name', 'quiz_name']
    list_filter = ['topic_name', 'quiz_name']
    exclude = ['quiz_name', 'topic_name']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('new/<int:add_question>/<str:add_option>/<str:add_is_correct>/', self.add_new_option)
        ]
        print(urls)
        return custom_urls + urls

    def add_new_option(self, request, add_question, add_option, add_is_correct):
        correct = False
        if add_is_correct == 'cor':
            correct = True
        q = Question.objects.filter(id=add_question).first()
        self.model.objects.create(question=q, answer_text=add_option, is_correct=correct)
        self.message_user(request, 'Ответ успешно добавлен!')
        return HttpResponseRedirect(f"/admin/quiz/option/?question__id={add_question}")
