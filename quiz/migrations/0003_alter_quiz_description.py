# Generated by Django 5.1.7 on 2025-07-11 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_alter_attempts_date_attempted_alter_quiz_added_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='description',
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
    ]
