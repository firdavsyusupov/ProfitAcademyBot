# Generated by Django 5.1.6 on 2025-02-13 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=100)),
                ('telegram', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=50)),
                ('current_time', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'users',
                'managed': False,
            },
        ),
    ]
