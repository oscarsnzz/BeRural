# Generated by Django 5.1.2 on 2024-12-11 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relecloud', '0003_alter_cruise_destinations'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='destinations/'),
        ),
        migrations.AlterField(
            model_name='cruise',
            name='destinations',
            field=models.ManyToManyField(related_name='cruises', to='relecloud.destination'),
        ),
    ]
