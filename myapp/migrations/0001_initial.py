# Generated by Django 3.2.25 on 2024-12-16 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Count',
            fields=[
                ('id', models.CharField(max_length=36, primary_key=True, serialize=False)),
                ('device_id', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('camera_id', models.CharField(max_length=255)),
                ('date', models.DateTimeField()),
            ],
        ),
    ]
