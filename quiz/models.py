from django.db import models
from accounts.models import User
from django.db.models import CharField, ForeignKey, BooleanField, TextField, DateTimeField
from django.utils.html import format_html
from datetime import datetime
from django.utils import timezone


class Topic(models.Model):
    name = CharField(max_length=200, unique=True, verbose_name='НАБОР')
    about = CharField(max_length=200, null=True, blank=True, verbose_name='Описание')
    notice = TextField(max_length=200, null=True, blank=True, verbose_name='Примечание')
    trash_bin = BooleanField(default=False, editable=False)

    class Meta:
        verbose_name = 'Набор тестов'
        verbose_name_plural = 'Наборы тестов'

    def __str__(self):
        return self.name


class Quiz(models.Model):
    name = CharField(max_length=200, verbose_name='ТЕСТ', unique=True)
    topic = ForeignKey(Topic, verbose_name='НАБОР', on_delete=models.SET_NULL, null=True, blank=True)
    editing = BooleanField(default=True, verbose_name='Выбран для редактирования')

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def question_text(self):
        try:
            Quiz.objects.filter(name=self.name)[0:1].get()
            qs = self.question_set.all().values()
            count = self.question_set.count()
            html_open = '<span><b><ul style="display: inline; text-align: left;">'
            html_close = '</ul></b></span>'
            if count > 0:
                for i in qs:
                    if i["accepted"] == False:
                        symbol = '<img src="/static/admin/img/icon-no.svg" alt="Нет">'
                    else:
                        symbol = '<img src="/static/admin/img/icon-yes.svg" alt="Да">'
                    html_tmp = '<li><pre style="padding-left: 0; margin: 0;">' + f'{symbol}' + '  ' + f'{i["text"]}' + '</pre></li>'
                    html_open += html_tmp
                html_ok = html_open + html_close
            else:
                html_ok = '<span><img src="/static/admin/img/icon-alert.svg" alt="Упс!">Вопросы не заданы</span>'
        except Quiz.DoesNotExist:
            html_ok = '<span><img src="/static/admin/img/icon-alert.svg" alt="Упс!">Сохраните ТЕСТ!</span>'
        return format_html(html_ok)

    question_text.short_description = "Вопросы теста"

    def __str__(self):
        return self.name


class Question(models.Model):
    text = CharField(max_length=500, verbose_name='ВОПРОС')
    quiz = ForeignKey(Quiz, verbose_name='ТЕСТ', on_delete=models.CASCADE)
    topic_name = ForeignKey(Topic, verbose_name='НАБОР', on_delete=models.SET_NULL, null=True, blank=True)
    accepted = BooleanField(default=False, verbose_name='Активирован')

    class Meta:
        verbose_name = 'Вопрос-Ответы'
        verbose_name_plural = 'Вопросы-Ответы'

    def save(self, *args, **kwargs):
        self.topic_name = self.quiz.topic
        super().save(*args, **kwargs)

    def option_text(self):
        try:
            Question.objects.filter(text=self)[0:1].get()
            qs = self.option_set.all().values()
            count = self.option_set.count()
            html_open = '<span><b><ul style="display: inline; text-align: left;">'
            html_close = '</ul></b></span>'
            if count > 0:
                for i in qs:
                    if i["is_correct"] == False:
                        symbol = '<img src="/static/admin/img/icon-no.svg" alt="Нет">'
                    else:
                        symbol = '<img src="/static/admin/img/icon-yes.svg" alt="Да">'
                    html_tmp = '<li style="list-style-type: none;"><pre style="padding-left: 0; margin: 0;">' + f'{symbol}' + '  ' + f'{(i["answer_text"])}' + '</pre></li>'
                    html_open += html_tmp
                html_ok = html_open + html_close
            else:
                html_ok = '<span><img src="/static/admin/img/icon-alert.svg" alt="Упс!">Ответы не заданы</span>'
        except Question.DoesNotExist:
            html_ok = '<span><img src="/static/admin/img/icon-alert.svg" alt="Упс!">Сохраните ВОПРОС!</span>'
        return format_html(html_ok)

    option_text.short_description = "Варианты ответов"

    def __str__(self):
        return self.text


class Option(models.Model):
    answer_text = CharField(max_length=200,  verbose_name='Ответ', null=True, blank=True)
    question = ForeignKey(Question,  verbose_name='Вопрос', on_delete=models.CASCADE)
    quiz_name = CharField(max_length=200, verbose_name='ТЕСТ', null=True, blank=True)
    topic_name = CharField(max_length=200, verbose_name='НАБОР', null=True, blank=True)
    is_correct = BooleanField(default=False, verbose_name='правильный ответ')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def save(self, *args, **kwargs):
        if self.quiz_name is None:
            qstn = Question.objects.filter(id=self.question_id).values().first()
            qz_id = qstn['quiz_id']
            qz = Quiz.objects.filter(id=qz_id).values().first()
            self.quiz_name = qz['name']
            tp_id = qz['topic_id']
            tp = Topic.objects.filter(id=tp_id).values().first()
            self.topic_name = tp['name']
        super().save(*args, **kwargs)

    def __str__(self):
        return self.answer_text


class QuestionMark(models.Model):
    user = ForeignKey(User, verbose_name="Студент", on_delete=models.CASCADE)
    question = ForeignKey(Question, verbose_name="Вопрос из теста", on_delete=models.CASCADE)
    done_correct = BooleanField()
    user_answer = CharField(max_length=200, verbose_name="Ответы студента", null=True, blank=True)
    corr_answer = CharField(max_length=200, verbose_name="Ответы на вопрос", null=True, blank=True)
    processed = BooleanField(default=False)


    def get_corr_answer(self):
        correct_options = Option.objects.filter(question=self.question).filter(is_correct=True).order_by('id').values('id')
        # correct_options = Option.objects.filter(question=self.question).filter(is_correct=True).order_by('id').values('id', 'answer_text')
        self.corr_answer = []
        for obj in correct_options:
            self.corr_answer.append(str(obj['id']))

    def eval_question(self):
        if list(self.user_answer) == list(self.corr_answer):
            self.done_correct = True
        else:
            self.done_correct = False

    def save(self, *args, **kwargs):
        self.get_corr_answer()
        self.eval_question()
        super().save(*args, **kwargs)


class TestMark(models.Model):
    user = ForeignKey(User, verbose_name="Студент", on_delete=models.CASCADE)
    topic = CharField(max_length=200, verbose_name='Набор', null=True, blank=True)
    quiz = CharField(max_length=200, verbose_name='Тест', null=True, blank=True)
    score = CharField(max_length=50, verbose_name='Оценка', null=True, blank=True)
    # date = DateTimeField(default=datetime.now, blank=True)
    date = DateTimeField(default=timezone.now, blank=True)


class ErrorObject(models.Model):
    user = ForeignKey(User, verbose_name="Студент", on_delete=models.CASCADE)
    question = ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE)
    test_mark = ForeignKey(TestMark, verbose_name="Результат теста", on_delete=models.CASCADE)
    test_date = DateTimeField(blank=True)
    wrong_answers = CharField(max_length=200, verbose_name='Неправильно', null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     qstn_mark = QuestionMark.objects.filter(question=self.question).filter(user=self.user).first()
    #     self.wrong_answers = qstn_mark.user_answer
    #     super().save(*args, **kwargs)
