# Generated by Django 3.2.9 on 2022-03-08 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0047_auto_20220125_1116'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-publication_date'], 'verbose_name': 'Actualité / Evènement', 'verbose_name_plural': 'Actualités / Evènements'},
        ),
    ]
