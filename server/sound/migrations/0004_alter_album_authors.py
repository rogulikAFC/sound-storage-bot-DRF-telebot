# Generated by Django 4.1.7 on 2023-04-01 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0002_alter_author_id'),
        ('sound', '0003_remove_sound_author_sound_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='authors',
            field=models.ManyToManyField(blank=True, to='author.author'),
        ),
    ]
