# Generated by Django 5.1.3 on 2024-12-09 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_entitylog_delete_userlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entitylog',
            name='details',
            field=models.TextField(blank=True, null=True),
        ),
    ]