# Generated by Django 3.2 on 2021-10-21 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='street',
            name='source',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='street',
            name='target',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]