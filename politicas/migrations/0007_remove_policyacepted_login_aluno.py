# Generated by Django 4.2.3 on 2024-02-07 22:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('politicas', '0006_policyacepted_login_aluno'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policyacepted',
            name='login_aluno',
        ),
    ]
