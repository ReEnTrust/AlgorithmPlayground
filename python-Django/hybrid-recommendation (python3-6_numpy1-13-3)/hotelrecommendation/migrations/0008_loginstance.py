# Generated by Django 2.2.1 on 2019-06-06 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotelrecommendation', '0007_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_instance_creation_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
