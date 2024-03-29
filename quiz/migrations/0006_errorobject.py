# Generated by Django 4.1.4 on 2022-12-31 00:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0005_testmark'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorObject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_date', models.DateTimeField(blank=True)),
                ('wrong_answers', models.CharField(blank=True, max_length=200, null=True, verbose_name='Неправильно')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.question', verbose_name='Вопрос')),
                ('test_mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.testmark', verbose_name='Результат теста')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Студент')),
            ],
        ),
    ]
