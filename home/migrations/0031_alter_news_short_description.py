# Generated by Django 3.2.9 on 2021-12-17 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0030_auto_20211217_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='short_description',
            field=models.CharField(blank=True, max_length=510, null=True, verbose_name='description courte'),
        ),
    ]
