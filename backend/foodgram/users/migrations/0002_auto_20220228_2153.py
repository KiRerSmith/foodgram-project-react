# Generated by Django 2.2.19 on 2022-02-28 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ['pk'], 'verbose_name': 'подписку', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username'], 'verbose_name': 'пользователя', 'verbose_name_plural': 'Пользователи'},
        ),
    ]