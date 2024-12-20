# Generated by Django 5.1.3 on 2024-12-02 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_flight_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='name',
        ),
        migrations.AddField(
            model_name='user',
            name='accent_color',
            field=models.CharField(default='#7d0e85', max_length=7),
        ),
        migrations.AddField(
            model_name='user',
            name='is_dark_theme',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_transparent',
            field=models.BooleanField(default=False),
        ),
    ]
