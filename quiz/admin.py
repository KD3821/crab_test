from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from .models import *
from django.urls import reverse, path
from django.utils.http import urlencode
from django.utils.html import format_html
from html import escape
from django.contrib.auth.models import Group


admin.site.unregister(Group)


@admin.action(description='Отметить как ПРАВИЛЬНЫЙ ответ')
def make_correct(modeladmin, request, queryset):
    queryset.update(is_correct=True)


@admin.action(description='Отметить как НЕПРАВИЛЬНЫЙ ответ')
def make_incorrect(modeladmin, request, queryset):
    queryset.update(is_correct=False)


def unbound_option_text(obj):
    return True


class QuestionInline(admin.StackedInline):
    model = Question
    fields = ['text', 'topic_name', 'quiz', 'accepted', 'option_text', 'admin_option_text', unbound_option_text, 'view_answers_href']
    readonly_fields = ['accepted', 'option_text', 'admin_option_text', unbound_option_text, 'view_answers_href']
    raw_id_fields = ['quiz']

    extra = 0

    def view_answers_href(self, obj):
        try:
            Question.objects.filter(text=obj)[0:1].get()
            count = obj.option_set.count()
            url = (
                    reverse("admin:quiz_option_changelist")
                    + "?"
                    + urlencode({"question__id": f"{obj.id}"})
            )
            return format_html('всего ответов: {} <br><a href="{}" class="addlink">'
                               '<button type="button" class="button">Добавить/редактировать ОТВЕТЫ &nbsp;| &nbsp;Активировать ВОПРОС</button></a>',
                               count, url)
        except Question.DoesNotExist:
            return format_html('Добавление | Редактирование ОТВЕТОВ возможно только после сохранения вопроса.'
                               '(кнопка "Сохранить" внизу страницы)')

    view_answers_href.short_description = "Подробнее"

    def admin_option_text(self, obj):
        return True

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': ('id', 'text', 'quiz', 'accepted')
            }),
            ('ответы', {
                'classes': ('collapse',),
                'fields': ('option_text',  'view_answers_href'),
            }),
        )
        return fieldsets


class QuizInline(admin.StackedInline):
    model = Quiz
    extra = 0




@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    change_form_template = 'admin/topics_change_form.html'

    list_display = ['view_edit_test_link', 'view_tests_link']
    inlines = [QuizInline, QuestionInline]
    exclude = ['trash_bin']

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('filter/<str:search_term>/', self.my_filter_test)
    #     ]
    #     return custom_urls + urls
    #
    # def my_filter_test(self, request, obj):
    #     pass

    def _response_post_save(self, request, obj):
        post_url = f'/admin/quiz/topic/{obj.id}/change/'
        return HttpResponseRedirect(post_url)

    def view_tests_link(self, obj):
        count = obj.quiz_set.count()
        return format_html('всего тестов: {} ', count)

    view_tests_link.short_description = "Тесты"

    def view_edit_test_link(self, obj):
        url = (reverse("admin:quiz_topic_changelist") + f'{obj.id}' + '/change/')
        return format_html('<a href="{}"><button type="button" class="button" style="background-color: pink; '
                           'color: blue;">{}</button></a>', url, obj.name)

    view_edit_test_link.short_description = "Набор тестов"

    def delete_queryset(self, request, queryset):
        if queryset[0].trash_bin == False:
            try:
                Topic.objects.filter(trash_bin=True)[0:1].get()
            except Topic.DoesNotExist:
                Topic.objects.create(name='No Name', trash_bin=True)
            quiz_qs = Quiz.objects.filter(topic=queryset[0].id)
            topic_qs = Topic.objects.filter(trash_bin=True).first()
            quiz_qs.update(topic=topic_qs.id)
            self.message_user(request, f'НАБОР "{queryset[0].name}" удален - при наличии ТЕСТОВ, '
                                       f'они были перенесены в НАБОР "No Name" (выполняет функцию "Корзина")!',
                              messages.WARNING)
            queryset.delete()
        else:
            self.message_user(request, f'Невозможно удалить НАБОР "{queryset[0].name}", т.к. он выполняет функцию "Корзина"!',
                              messages.ERROR)
            self.message_user(request, f'Вы можете удалить ТЕСТЫ внутри НАБОРА "{queryset[0].name}", но не сам набор.',
                              messages.WARNING)

    def delete_model(self, request, obj):
        queryset = Topic.objects.filter(name=obj.name)
        self.delete_queryset(request, queryset)

    def save_model(self, request, obj, form, change):
        if obj.trash_bin == True:
            obj.name = 'No Name'
        obj.save()


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    change_list_template = 'admin/quizes_change_list.html'

    list_display = ['name', 'topic', 'view_questions_link']
    list_filter = ['topic']

    def has_module_permission(self, request):
        return False

    def view_questions_link(self, obj):
        count = obj.question_set.count()
        return format_html('всего вопросов: {} ', count)

    view_questions_link.short_description = "Вопросы"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'accepted', 'quiz', 'view_answers_link']
    exclude = ['topic_name']
    readonly_fields = ['accepted']

    def has_module_permission(self, request):
        return False

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
            path('nosave/<int:save_question>/', self.exit_options)
        ]
        return custom_urls + urls

    def add_new_option(self, request, add_question, add_option, add_is_correct):
        correct = False
        if add_is_correct == 'cor':
            correct = True
        q = Question.objects.filter(id=add_question).first()
        add_option_ok = escape(add_option)
        self.model.objects.create(question=q, answer_text=add_option_ok, is_correct=correct)
        self.message_user(request, 'Ответ успешно добавлен!')
        return HttpResponseRedirect(f"/admin/quiz/option/?question__id={add_question}")

    def save_options(self, request, save_question):
        q = Question.objects.filter(id=save_question).first()
        t = Topic.objects.filter(name=q.topic_name).first()
        try:
            Option.objects.filter(question=q).filter(is_correct=True)[0:1].get()
            a_qs = Option.objects.filter(question=q).filter(is_correct=True)
            b_qs = Option.objects.filter(question=q)
            if len(a_qs) < len(b_qs):
                self.message_user(request, 'Вопрос активирован - ответы успешно сохранены!')
                q.accepted = True
                q.save()
                return HttpResponseRedirect(f"/admin/quiz/topic/{t.id}/change/")
            elif len(b_qs) == 1:
                self.message_user(request, 'Вопрос не активирован - кол-во ответов должно быть больше 1!',
                                  messages.ERROR)
            elif len(a_qs) == len(b_qs):
                self.message_user(request, 'Вопрос не активирован - хотя бы 1 ответ должен быть неправильным!',
                                  messages.ERROR)
            q.accepted = False
            q.save()
            return HttpResponseRedirect(f"/admin/quiz/option/?question__id={save_question}")
        except Option.DoesNotExist:
            self.message_user(request, 'Вопрос не активирован - должен быть хотя бы 1 правильный ответ!',
                              messages.ERROR)
            q.accepted = False
            q.save()
            return HttpResponseRedirect(f"/admin/quiz/option/?question__id={save_question}")

    def exit_options(self, request, save_question):
        q = Question.objects.filter(id=save_question).first()
        t = Topic.objects.filter(name=q.topic_name).first()
        if q.accepted == False:
            self.message_user(request, 'Вопрос не активирован - для активации необходимо нажать зеленую кнопку'
                                       ' "Активировать вопрос" на странице редактирования ответов!', messages.WARNING)
        else:
            try:
                Option.objects.filter(question=q)[0:1].get()
                self.save_options(request, save_question)
            except Option.DoesNotExist:
                q.accepted = False
                q.save()
                self.message_user(request, 'Вопрос деактивирован, так как не добавлены ответы!',
                                  messages.ERROR)
        return HttpResponseRedirect(f"/admin/quiz/topic/{t.id}/change/")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        q_id = request.GET['question__id']
        qs_q = Question.objects.filter(id=q_id).select_related('topic_name', 'quiz').first()
        question_text = qs_q.text
        question_quiz = qs_q.quiz
        question_topic = qs_q.topic_name
        if qs_q.accepted == True:
            question_accepted = 'ДА'
        else:
            question_accepted = 'НЕТ'
        extra_context['question_text'] = question_text
        extra_context['question_quiz'] = question_quiz
        extra_context['question_topic'] = question_topic
        extra_context['question_accepted'] = question_accepted
        return super().changelist_view(request, extra_context=extra_context)
