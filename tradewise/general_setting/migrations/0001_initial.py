# Generated by Django 5.2 on 2025-04-18 19:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("profile_id", models.AutoField(primary_key=True, serialize=False)),
                ("timezone", models.CharField(max_length=50)),
                ("currency", models.CharField(max_length=3)),
                ("is_active", models.CharField(default="Y", max_length=1)),
                (
                    "customer_id",
                    models.ForeignKey(
                        db_column="customer_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "auth_login_customer_profile",
            },
        ),
    ]
