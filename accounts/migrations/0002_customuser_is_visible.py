# Generated by Django 5.1 on 2024-12-28 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='is_visible'),
        ),
    ]