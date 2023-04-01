# Generated by Django 4.1.7 on 2023-04-01 06:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0002_alter_author_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True),
        ),
    ]