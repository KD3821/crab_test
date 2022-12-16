from django.contrib import admin
from .models import *


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic']
    list_filter = ['topic']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'id', 'quiz']
    list_filter = ['topic_name', 'quiz']
    exclude = ['topic_name']

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['answer_text', 'question', 'is_correct', 'question_id', 'topic_name', 'quiz_name']
    list_filter = ['topic_name', 'quiz_name']
    exclude = ['quiz_name', 'topic_name']

