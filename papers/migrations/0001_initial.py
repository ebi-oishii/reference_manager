# Generated by Django 5.1 on 2024-11-22 07:35

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.TextField(max_length=255, verbose_name='first_name')),
                ('last_name', models.TextField(max_length=255, verbose_name='last_name')),
            ],
            options={
                'db_table': 'author',
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True, verbose_name='publisher name')),
            ],
            options={
                'db_table': 'publisher',
            },
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=255, verbose_name='name')),
            ],
            options={
                'db_table': 'university',
            },
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('paper_id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='paper_id')),
                ('title', models.TextField(verbose_name='title')),
                ('arxiv', models.TextField(blank=True, null=True, unique=True, verbose_name='arxiv_id')),
                ('doi', models.TextField(blank=True, null=True, unique=True, verbose_name='doi')),
                ('published_date', models.DateField(verbose_name='published_date')),
                ('authors', models.ManyToManyField(to='papers.author', verbose_name='author')),
                ('bookmark_user', models.ManyToManyField(related_name='bookmark_paper', to=settings.AUTH_USER_MODEL, verbose_name='bookmark_user')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='papers.publisher', verbose_name='publisher')),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='affiliation',
            field=models.ManyToManyField(blank=True, null=True, to='papers.university', verbose_name='affiliation'),
        ),
    ]
