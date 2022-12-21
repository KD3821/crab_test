from django.db import models
from django.db.models import CharField, ForeignKey, BooleanField
from django.utils.html import format_html
from html import escape, unescape


class Topic(models.Model):
    name = CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Набор тестов'
        verbose_name_plural = 'Наборы тестов'

    def __str__(self):
        return self.name


class Quiz(models.Model):
    name = CharField(max_length=200, verbose_name='ТЕСТ', unique=True)
    topic = ForeignKey(Topic, verbose_name='НАБОР', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.name


class Question(models.Model):
    text = CharField(max_length=500)
    quiz = ForeignKey(Quiz, verbose_name='ТЕСТ', on_delete=models.SET_NULL, null=True, blank=True)
    topic_name = ForeignKey(Topic, verbose_name='НАБОР', on_delete=models.SET_NULL, null=True, blank=True)
    accepted = BooleanField(default=False, verbose_name="Добавлен в тест")

    class Meta:
        verbose_name = 'Вопрос-Ответы'
        verbose_name_plural = 'Вопросы-Ответы'

    def save(self, *args, **kwargs):
        self.topic_name = self.quiz.topic
        super().save(*args, **kwargs)

    def option_text(self):
        try:
            q = Question.objects.filter(text=self)[0:1].get()
            if q:
                qs = self.option_set.all().values()
                count = self.option_set.count()
                html_open = '<span><b><ul style="display: inline; text-align: left;">'
                html_close = '</ul></b></span>'
                if count > 0:
                    for i in qs:
                        if i["is_correct"] == False:
                            symbol = '<img src="/static/admin/img/icon-no.svg" alt="Да">'
                        else:
                            symbol = '<img src="/static/admin/img/icon-yes.svg" alt="Да">'
                        html_tmp = '<li><pre style="padding-left: 0; margin: 0;">' + f'{symbol}' + '  ' + f'{i["answer_text"]}' + '</pre></li>'
                        html_open += html_tmp
                    html_ok = html_open + html_close
                else:
                    html_ok = '<span><img src="/static/admin/img/icon-alert.svg" alt="Упс!">Ответы не заданы</span>'
        except Question.DoesNotExist:
            html_ok = '<span><img src="/static/admin/img/icon-alert.svg" alt="Упс!">Сохраните ВОПРОС!</span>'
        return format_html(html_ok)


    def __str__(self):
        return self.text


class Option(models.Model):
    answer_text = CharField(max_length=200,  verbose_name='Ответ', null=True, blank=True)
    question = ForeignKey(Question,  verbose_name='Вопрос', on_delete=models.CASCADE)
    is_correct = BooleanField(default=False, verbose_name='правильный ответ')
    quiz_name = CharField(max_length=200, verbose_name='ТЕСТ', null=True, blank=True)
    topic_name = CharField(max_length=200, verbose_name='НАБОР', null=True, blank=True)

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
