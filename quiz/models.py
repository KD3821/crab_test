from django.db import models
from django.db.models import CharField, ForeignKey, BooleanField

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
        # return self.option_set.all()
        qs = self.option_set.all().values()
        count = self.option_set.count()
        return {'count': count, 'options': qs}

    def __str__(self):
        return self.text


class Option(models.Model):
    answer_text = CharField(max_length=200,  verbose_name='Ответ')
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
