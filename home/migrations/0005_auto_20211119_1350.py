# Generated by Django 3.2.9 on 2021-11-19 13:50

from django.db import migrations, models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20211117_0902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheme',
            name='link',
        ),
        migrations.AddField(
            model_name='scheme',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(form_classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())], blank=True, help_text='Cette description sera le corps de la page de détail du dispositif, il est inutil de le remplir si il y a un lien externe', verbose_name='description'),
        ),
        migrations.AddField(
            model_name='scheme',
            name='external_link',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='lien externe'),
        ),
        migrations.AddField(
            model_name='scheme',
            name='short_description',
            field=models.CharField(default='Description à rédiger', max_length=510, verbose_name='description courte'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(form_classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())], blank=True, verbose_name='contenu'),
        ),
    ]
