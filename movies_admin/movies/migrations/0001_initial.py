# Generated by Django 3.2.6 on 2021-09-07 03:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FilmWork',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=250, verbose_name='title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('creation_date', models.DateField(blank=True, null=True, verbose_name='creation date')),
                ('certificate', models.TextField(blank=True, null=True, verbose_name='certificate')),
                ('file_path', models.FileField(blank=True, null=True, upload_to='film_works/', verbose_name='file')),
                ('rating', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)], verbose_name='rating')),
                ('type', models.CharField(choices=[('movie', 'movie'), ('tv_show', 'TV Show')], default='movie', max_length=20, verbose_name='type')),
            ],
            options={
                'verbose_name': 'Film',
                'verbose_name_plural': 'Films',
                'db_table': '"content"."film_work"',
                'ordering': ['-rating'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'Genre',
                'verbose_name_plural': 'Genres',
                'db_table': '"content"."genre"',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=200, verbose_name='full_name')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='birth_date')),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'Persons',
                'db_table': '"content"."person"',
                'ordering': ['full_name'],
            },
        ),
        migrations.CreateModel(
            name='PersonFilmWork',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('actor', 'actor'), ('writer', 'writer'), ('director', 'director')], max_length=50, verbose_name='role')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('film_work', models.ForeignKey(db_column='film_work_id', on_delete=django.db.models.deletion.CASCADE, related_name='persons', to='movies.filmwork')),
                ('person', models.ForeignKey(db_column='person_id', on_delete=django.db.models.deletion.CASCADE, related_name='film_works', to='movies.person')),
            ],
            options={
                'verbose_name': 'Connection Film to Person',
                'verbose_name_plural': 'Connections Film to Person',
                'db_table': '"content"."person_film_work"',
                'ordering': ['role'],
                'unique_together': {('film_work', 'person', 'role')},
            },
        ),
        migrations.CreateModel(
            name='GenreFilmWork',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('film_work', models.ForeignKey(db_column='film_work_id', on_delete=django.db.models.deletion.CASCADE, related_name='film_genres', to='movies.filmwork')),
                ('genre', models.ForeignKey(db_column='genre_id', on_delete=django.db.models.deletion.CASCADE, related_name='film_works', to='movies.genre')),
            ],
            options={
                'verbose_name': 'Genre',
                'verbose_name_plural': 'Genres',
                'db_table': '"content"."genre_film_work"',
                'ordering': ['genre__name'],
                'unique_together': {('film_work', 'genre')},
            },
        ),
    ]