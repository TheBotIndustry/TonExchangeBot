# Generated by Django 4.0.2 on 2022-03-25 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('currency', models.TextField(verbose_name='Валюта')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Список категорий',
                'db_table': 'categories',
            },
        ),
    ]
