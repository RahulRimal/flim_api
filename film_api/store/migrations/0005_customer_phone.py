# Generated by Django 4.1.2 on 2022-10-08 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_address_zipcode_alter_address_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='phone',
            field=models.CharField(default=7897345678, max_length=11),
            preserve_default=False,
        ),
    ]
