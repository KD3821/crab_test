from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from .models import *
from django.urls import reverse, path
from django.utils.http import urlencode
from django.utils.html import format_html


@admin.action(description='Отметить как правильный ответ')
def make_correct(modeladmin, request, queryset):
    queryset.update(is_correct=True)

@admin.action(description='Неправильный ответ')
def make_incorrect(modeladmin, request, queryset):
    queryset.update(is_correct=False)


class QuestionInline(admin.TabularInline):
    model = Question


class QuizInline(admin.TabularInline):
    model = Quiz


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['view_edit_test_link', 'view_tests_link']
    inlines = [QuizInline, QuestionInline]

    def view_tests_link(self, obj):
        count = obj.quiz_set.count()
        url = (
                reverse("admin:quiz_quiz_changelist")
                + "?"
                + urlencode({"topic__id": f"{obj.id}"})
        )
        return format_html('всего тестов: {} <a href="{}"><button type="button" class="button">См.список</button></a>',
                           count, url)

    view_tests_link.short_description = "Тесты"

    def view_edit_test_link(self, obj):
        url = (reverse("admin:quiz_topic_changelist") + f'{obj.id}' + '/change/')
        return format_html('<a href="{}"><button type="button" class="button" style="background-color: pink; '
                           'color: blue;">{}</button></a>', url, obj.name)

    view_edit_test_link.short_description = "Набор тестов"



@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic', 'view_questions_link']
    list_filter = ['topic']
    # inlines = [QuestionInline]

    def has_module_permission(self, request):
        return False

    def view_questions_link(self, obj):
        count = obj.question_set.count()
        url = (
                reverse("admin:quiz_question_changelist")
                + "?"
                + urlencode({"quiz__id": f"{obj.id}"})
        )
        return format_html('всего вопросов: {} <a href="{}"><button type="button" class="button">'
                           'См.список</button></a>', count, url)

    view_questions_link.short_description = "Вопросы"



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'accepted', 'quiz', 'view_answers_link']
    list_filter = ['topic_name', 'quiz']
    exclude = ['topic_name']

    def view_answers_link(self, obj):
        count = obj.option_set.count()
        url = (
                reverse("admin:quiz_option_changelist")
                + "?"
                + urlencode({"question__id": f"{obj.id}"})
        )
        return format_html('всего ответов: {} <br><a href="{}" class="addlink">'
                           '<button type="button" class="button">Добавить ответ</button></a>', count, url)

    view_answers_link.short_description = "Ответы"

    def get_form(self, request, obj=None, **kwargs):
        form = super(QuestionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['quiz'].queryset = Quiz.objects.filter(topic__name=obj.topic_name)
        return form

    def has_add_permission(self, request):
        return False


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    change_list_template = 'admin/options_change_list.html'

    list_display = ['answer_text', 'is_correct', 'question', 'question_id', 'topic_name', 'quiz_name']
    list_filter = ['topic_name', 'quiz_name']
    exclude = ['quiz_name', 'topic_name']
    actions = [make_correct, make_incorrect]

    def has_module_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('new/<int:add_question>/<str:add_option>/<str:add_is_correct>/', self.add_new_option),
            path('save/<int:save_question>/', self.save_options),
        ]
        return custom_urls + urls

    def add_new_option(self, request, add_question, add_option, add_is_correct):
        correct = False
        if add_is_correct == 'cor':
            correct = True
        q = Question.objects.filter(id=add_question).first()
        self.message_user(request, 'Ответ успешно добавлен!')
        self.model.objects.create(question=q, answer_text=add_option, is_correct=correct)
        return HttpResponseRedirect(f"/admin/quiz/option/?question__id={add_question}")


    def save_options(self, request, save_question):
        print(save_question)
        q = Question.objects.filter(id=save_question).first()
        a_qs = Option.objects.filter(question=q).filter(is_correct=True)
        b_qs = Option.objects.filter(question=q)
        try:
            a_qs[0:1].get()
            if len(a_qs) < len(b_qs):
                self.message_user(request, 'Вопрос добавлен в тест - ответы успешно сохранены!')
                q.accepted = True
                q.save()
                return HttpResponseRedirect(f"/admin/quiz/question/")
            if len(b_qs) == 1:
                self.message_user(request, 'Вопрос не добавлен в тест - кол-во ответов должно быть больше 1!',
                                  messages.ERROR)
                return HttpResponseRedirect(f"/admin/quiz/option/?question__id={save_question}")
            if len(a_qs) == len(b_qs):
                self.message_user(request, 'Вопрос не добавлен в тест - хотя бы 1 ответ должен быть неправильным!',
                                  messages.ERROR)
                return HttpResponseRedirect(f"/admin/quiz/option/?question__id={save_question}")
        except Option.DoesNotExist:
            self.message_user(request, 'Вопрос не добавлен в тест - должен быть хотя бы 1 правильный ответ!',
                              messages.ERROR)
            return HttpResponseRedirect(f"/admin/quiz/option/?question__id={save_question}")


    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        q_id = request.GET['question__id']
        qs_q = Question.objects.filter(id=q_id).select_related('topic_name', 'quiz').first()
        question_text = qs_q.text
        question_quiz = qs_q.quiz
        question_topic = qs_q.topic_name
        extra_context['question_text'] = question_text
        extra_context['question_quiz'] = question_quiz
        extra_context['question_topic'] = question_topic

        return super().changelist_view(request, extra_context=extra_context)
