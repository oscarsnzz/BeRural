# Generated by Django 5.1.2 on 2025-05-04 16:24

import shortuuid.main
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("relecloud", "0015_remove_cruise_destinations_remove_review_cruise_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatgroup",
            name="group_name",
            field=models.CharField(
                default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True
            ),
        ),
    ]
