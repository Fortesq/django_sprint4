# Generated by Django 3.2.16 on 2023-11-11 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20231110_2251'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment_text',
            new_name='text',
        ),
    ]