from django.db import models
from django.db.models import CharField, ForeignKey, BooleanField

class Topic(models.Model):
    name = CharField(max_length=200)

    class Meta:
        verbose_name = 'Набор тестов'
        verbose_name_plural = 'Наборы тестов'

    def __str__(self):
        return self.name


class Quiz(models.Model):
    name = CharField(max_length=200)
    topic = ForeignKey(Topic, verbose_name='НАБОР', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.name


class Question(models.Model):
    text = CharField(max_length=500)
    quiz = ForeignKey(Quiz, verbose_name='ТЕСТ', on_delete=models.SET_NULL, null=True, blank=True)
    topic_name = CharField(max_length=200, verbose_name='НАБОР', null=True, blank=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def save(self, *args, **kwargs):
        if self.topic_name is None:
            qz = Quiz.objects.filter(id=self.quiz_id).values().first()
            tp_id = qz['topic_id']
            tp = Topic.objects.filter(id=tp_id).values().first()
            self.topic_name = tp['name']
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text


class Option(models.Model):
    answer_text = CharField(max_length=200)
    question = ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = BooleanField(default=False)
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
        return f'{self.answer_text} - {self.question}'
