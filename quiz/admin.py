from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from .models import *
from django.urls import reverse, path
from django.utils.http import urlencode
from django.utils.html import format_html
from html import escape
from django.contrib.auth.models import Group


admin.site.unregister(Group)

@admin.register(QuestionMark)
class QuestionMarkAdmin(admin.ModelAdmin):
    list_display = ['question', 'user', 'get_test_name', 'done_correct', 'user_answer', 'corr_answer']

    def get_test_name(self, obj):
        q = Question.objects.filter(id=obj.question.id).first()
        test = Quiz.objects.filter(id=q.quiz.id).first()
        return test


@admin.register(TestMark)
class TestMarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'quiz', 'score', 'date']


@admin.register(ErrorObject)
class ErrorObjectAdmin(admin.ModelAdmin):
    list_display = ['question', 'user', 'test_mark', 'test_date', 'wrong_answers']


@admin.action(description='Отметить как ПРАВИЛЬНЫЙ ответ')
def make_correct(modeladmin, request, queryset):
    queryset.update(is_correct=True)


@admin.action(description='Отметить как НЕПРАВИЛЬНЫЙ ответ')
def make_incorrect(modeladmin, request, queryset):
    queryset.update(is_correct=False)


def unbound_option_text(obj):
    return True


class QuestionInline(admin.TabularInline):
    model = Question
    fields = ['text', 'topic_name', 'quiz', 'accepted', 'editing_mode', 'option_text', 'admin_option_text', unbound_option_text, 'view_answers_href']
    readonly_fields = ['accepted', 'option_text', 'admin_option_text', unbound_option_text, 'view_answers_href']
    raw_id_fields = ['quiz']
    extra = 0
    ordering = ['quiz']

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

    def get_queryset(self, request):
        queryset = super(QuestionInline, self).get_queryset(request)
        editing_mode_qs = queryset.filter(quiz__editing=True)
        queryset = editing_mode_qs
        return queryset


def unbound_question_text(obj):
    return True


class QuizInline(admin.StackedInline):
    model = Quiz
    extra = 0
    fields = ['name', 'editing', 'topic', 'question_text', 'admin_question_text', unbound_question_text, 'view_questions_href']
    readonly_fields = ['editing', 'question_text', 'admin_question_text', unbound_question_text, 'view_questions_href']
    raw_id_fields = ['topic']

    def admin_question_text(self, obj):
        return True

    def view_questions_href(self, obj):
        try:
            Quiz.objects.filter(name=obj.name)[0:1].get()
            count = obj.question_set.count()
            count_accepted = obj.question_set.filter(accepted=True).count()
            return format_html('всего вопросов: {} ( активировано: {} )', count, count_accepted)
        except Quiz.DoesNotExist:
            return format_html('Добавление | Редактирование ВОПРОСОВ возможно только после сохранения ТЕСТА.'
                               '(кнопка "Сохранить" внизу страницы)')

    view_questions_href.short_description = "ИТОГО"

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': ('name', 'topic', 'editing')
            }),
            ('вопросы теста', {
                'classes': ('collapse',),
                'fields': ('question_text', 'view_questions_href'),
            }),
        )
        return fieldsets


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    change_form_template = 'admin/topics_change_form.html'

    list_display = ['view_edit_test_link', 'view_about_test_link', 'view_tests_link']
    inlines = [QuizInline, QuestionInline]
    exclude = ['trash_bin']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:topic_id>/change/<str:test_filter>/', self.my_filter)
        ]
        return custom_urls + urls

    def my_filter(self, request, topic_id, test_filter):
        qzs = Quiz.objects.filter(topic__id=topic_id)
        if test_filter == 'all_qzs_slctd':
            qzs.update(editing=True)
        else:
            quiz = qzs.filter(id=test_filter)
            qzs.update(editing=False)
            quiz.update(editing=True)
        return HttpResponseRedirect(f'/admin/quiz/topic/{topic_id}/change/')

    def change_view(self, request, object_id, form_url="",  extra_context=None):
        extra_context = extra_context or {}
        opts = self.model._meta
        extra_context['opts'] = opts
        extra_context['show_delete'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['add'] = True
        extra_context['change'] = True
        extra_context['is_popup'] = False
        extra_context['save_as'] = True
        extra_context['has_delete_permission'] = True
        extra_context['has_add_permission'] = True
        extra_context['has_change_permission'] = True
        extra_context['has_view_permission'] = True
        extra_context['has_editable_inline_admin_formsets'] = True
        extra_context['can_save'] = extra_context['has_change_permission'] or extra_context['change'] or extra_context['has_editable_inline_admin_formsets']
        extra_context['can_save_and_continue'] = not extra_context['is_popup'] and extra_context['can_save'] and extra_context['has_view_permission'] and extra_context['show_save_and_add_another']
        extra_context['can_change'] = extra_context['has_change_permission'] or extra_context['has_editable_inline_admin_formsets']
        obj_id = Topic.objects.filter(id=object_id).first()
        tests = Quiz.objects.filter(topic=obj_id)
        extra_context['tests'] = tests
        object_id = str(object_id)
        return self.changeform_view(request, object_id, form_url, extra_context=extra_context)


    def _response_post_save(self, request, obj):
        post_url = f'/admin/quiz/topic/{obj.id}/change/'
        try:
            Topic.objects.filter(trash_bin=True)[0:1].get()
        except Topic.DoesNotExist:
            Topic.objects.create(name='No Name', trash_bin=True,
                                 about='"Корзина" для тестов из удаленных НАБОРОВ (защищен от удаления, в остальном - обычный НАБОР)',
                                 notice='Вы можете восстановить любой ВОПРОС, но не ТЕСТ целиком. Для этого укажите в '
                                        'поле "ТЕСТ" нужный Вам ТЕСТ, и ВОПРОС будет перемещен в соответствующий '
                                        'НАБОР>>>ТЕСТ.')
        return HttpResponseRedirect(post_url)

    def view_tests_link(self, obj):
        count = obj.quiz_set.count()
        return format_html('всего тестов: {} ', count)

    view_tests_link.short_description = "Тесты"

    def view_about_test_link(self, obj):
        info = obj.about
        if obj.about is None:
            info = 'нет данных'
        return format_html('{}', info)

    view_about_test_link.short_description = "Описание"

    def view_edit_test_link(self, obj):
        url = (reverse("admin:quiz_topic_changelist") + f'{obj.id}' + '/change/')
        return format_html('<a href="{}"><button type="button" class="button" style="background-color: pink; '
                           'color: blue;">{}</button></a>', url, obj.name)

    view_edit_test_link.short_description = "Набор тестов"

    def delete_queryset(self, request, queryset):
        if queryset[0].trash_bin == False:
            quiz_qs = Quiz.objects.filter(topic=queryset[0].id)
            question_qs = Question.objects.filter(topic_name=queryset[0].id)
            topic_qs = Topic.objects.filter(trash_bin=True).first()
            quiz_qs.update(topic=topic_qs.id)
            question_qs.update(topic_name=topic_qs.id)
            self.message_user(request, f'НАБОР "{queryset[0].name}" удален - при наличии ТЕСТОВ, '
                                       f'они были перенесены в НАБОР "No Name" (выполняет функцию "Корзина")!',
                              messages.WARNING)
            queryset.delete()
        else:
            self.message_user(request, f'Невозможно удалить НАБОР "{queryset[0].name}", т.к. он выполняет функцию "Корзина"!',
                              messages.ERROR)
            self.message_user(request, f'Вы можете удалить ТЕСТЫ и/или ВОПРОСЫ внутри НАБОРА "{queryset[0].name}", но не сам набор.',
                              messages.WARNING)

    def delete_model(self, request, obj):
        queryset = Topic.objects.filter(name=obj.name)
        self.delete_queryset(request, queryset)

    def save_model(self, request, obj, form, change):
        if obj.trash_bin == True:
            obj.name = 'No Name'
            obj.about = '"Корзина" для тестов из удаленных НАБОРОВ (защищен от удаления, в остальном - обычный НАБОР)'
            obj.notice = 'Вы можете восстановить любой ВОПРОС, но не ТЕСТ целиком. Для этого укажите в поле "ТЕСТ" ' \
                         'нужный Вам ТЕСТ, и ВОПРОС будет перемещен в соответствующий НАБОР>>>ТЕСТ.'
        obj.save()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        all_qzs = Quiz.objects.all()
        all_qzs.update(editing=True)
        return super().changelist_view(request, extra_context=extra_context)


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
        extra_context['has_add_permission'] = True
        extra_context['has_editable_inline_admin_formsets'] = True
        return super().changelist_view(request, extra_context=extra_context)
