# Generated by Django 5.1.2 on 2025-05-02 18:34

import django.db.models.deletion
import shortuuid.main
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("relecloud", "0013_alter_chatgroup_group_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tareamudanza",
            options={"ordering": ["orden"]},
        ),
        migrations.AlterField(
            model_name="chatgroup",
            name="group_name",
            field=models.CharField(
                default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="tareamudanza",
            name="completada",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="tareamudanza",
            name="nombre",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="tareamudanza",
            name="orden",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="tareamudanza",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
