# Generated by Django 3.2.25 on 2024-12-28 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0012_auto_20241228_0953'),
    ]

    operations = [
        migrations.RunSQL(
            # Cette migration ne fait rien car les tables existent déjà
            "SELECT 1;",
            "SELECT 1;"
        ),
    ]
