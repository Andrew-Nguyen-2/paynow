# Generated by Django 3.2.8 on 2021-11-09 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_invoicehistory_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicehistory',
            name='organization_name',
            field=models.CharField(default='NO ORG', max_length=75),
        ),
    ]