# Generated by Django 4.1.2 on 2022-10-05 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name',
            field=models.CharField(default='Default Category', max_length=255),
            preserve_default=False,
        ),
    ]