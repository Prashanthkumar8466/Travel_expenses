# Generated by Django 5.0.6 on 2024-07-18 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Expenses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='status',
            field=models.TextField(default='pending'),
        ),
    ]
