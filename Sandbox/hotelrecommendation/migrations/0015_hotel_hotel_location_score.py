# Generated by Django 2.2.1 on 2019-07-04 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotelrecommendation', '0014_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='hotel_location_score',
            field=models.DecimalField(decimal_places=15, default=-1, max_digits=20),
        ),
    ]