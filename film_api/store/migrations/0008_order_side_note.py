# Generated by Django 4.1.2 on 2022-10-31 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_billinginfo_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='side_note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
