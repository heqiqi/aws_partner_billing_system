# Generated by Django 3.2.12 on 2023-05-30 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_auto_20230525_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='dept',
            name='account_id',
            field=models.IntegerField(blank=True, default=0, help_text='账号ID', null=True, verbose_name='账号ID'),
        ),
    ]
