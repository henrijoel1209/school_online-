# Generated by Django 3.2.25 on 2024-12-28 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0015_auto_20241227_1851'),
        ('student', '0008_auto_20241228_0847'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('file', models.FileField(blank=True, null=True, upload_to='assignments/')),
                ('max_points', models.FloatField(default=20)),
                ('due_date', models.DateTimeField()),
                ('date_add', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='school.cours')),
            ],
            options={
                'verbose_name': 'Devoir',
                'verbose_name_plural': 'Devoirs',
                'ordering': ['-due_date'],
            },
        ),
        migrations.CreateModel(
            name='StudentAssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_file', models.FileField(upload_to='assignment_submissions/')),
                ('submission_text', models.TextField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('score', models.FloatField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('submitted', 'Soumis'), ('graded', 'Noté'), ('late', 'En retard'), ('resubmit', 'À refaire')], default='submitted', max_length=20)),
                ('date_add', models.DateTimeField(auto_now_add=True)),
                ('date_update', models.DateTimeField(auto_now=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='student.studentassignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignment_submissions', to='student.student')),
            ],
            options={
                'verbose_name': 'Soumission de devoir',
                'verbose_name_plural': 'Soumissions de devoirs',
                'ordering': ['-submitted_at'],
                'unique_together': {('assignment', 'student')},
            },
        ),
    ]
