# Generated by Django 4.2.1 on 2023-05-21 02:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0008_remove_preferences_login_redirect_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='preferences',
            old_name='Ferramenta favorita',
            new_name='login_redirect',
        ),
    ]
