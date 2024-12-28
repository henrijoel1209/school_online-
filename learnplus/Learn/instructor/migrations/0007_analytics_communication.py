# Generated by Django 5.1.4 on 2024-12-28 14:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instructor', '0006_auto_20241227_1645'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('total_students', models.IntegerField(default=0)),
                ('active_students', models.IntegerField(default=0)),
                ('completion_rate', models.FloatField(default=0)),
                ('total_courses', models.IntegerField(default=0)),
                ('total_chapters', models.IntegerField(default=0)),
                ('total_lessons', models.IntegerField(default=0)),
                ('average_quiz_score', models.FloatField(default=0)),
                ('total_assignments', models.IntegerField(default=0)),
                ('graded_assignments', models.IntegerField(default=0)),
                ('student_messages', models.IntegerField(default=0)),
                ('forum_posts', models.IntegerField(default=0)),
                ('resource_downloads', models.IntegerField(default=0)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='instructor.instructor')),
            ],
            options={
                'verbose_name': 'Analytique',
                'verbose_name_plural': 'Analytiques',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('attachment', models.FileField(blank=True, null=True, upload_to='communications/')),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('announcement', 'Annonce'), ('reminder', 'Rappel'), ('feedback', 'Feedback'), ('notification', 'Notification')], max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('sent', 'Envoyé'), ('scheduled', 'Programmé')], default='draft', max_length=20)),
                ('scheduled_date', models.DateTimeField(blank=True, null=True)),
                ('instructor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='communications', to='instructor.instructor')),
                ('recipients', models.ManyToManyField(related_name='received_communications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Communication',
                'verbose_name_plural': 'Communications',
                'ordering': ['-date_sent'],
            },
        ),
    ]