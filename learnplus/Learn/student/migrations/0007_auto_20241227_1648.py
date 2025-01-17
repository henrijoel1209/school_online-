# Generated by Django 3.2.25 on 2024-12-27 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0006_auto_20241227_1645'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentresponse',
            options={'ordering': ['-date_add'], 'verbose_name': 'Student Response', 'verbose_name_plural': 'Student Responses'},
        ),
        migrations.AddField(
            model_name='studentresponse',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentresponse',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentresponse',
            name='score',
            field=models.FloatField(default=0),
        ),
    ]
