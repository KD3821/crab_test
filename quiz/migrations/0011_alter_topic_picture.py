# Generated by Django 4.1.4 on 2023-01-05 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0010_alter_topic_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='picture',
            field=models.ImageField(blank=True, default='', null=True, upload_to='topic_pics/'),
        ),
    ]