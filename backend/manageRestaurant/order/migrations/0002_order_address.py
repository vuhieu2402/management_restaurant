# Generated by Django 4.2.18 on 2025-02-20 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.CharField(default="Address", max_length=255),
        ),
    ]
