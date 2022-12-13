from django.db import models
from django.db.models import CharField, ForeignKey, BooleanField

class Topic(models.Model):
    name = CharField(max_length=200)


class Quiz(models.Model):
    name = CharField(max_length=200)
    topic = ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)


class Question(models.Model):
    text = CharField(max_length=500)
    quiz = ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True)


class Option(models.Model):
    text = CharField(max_length=200)
    question = ForeignKey(Question, on_delete=models.CASCADE)
    correct = BooleanField(default=False)
