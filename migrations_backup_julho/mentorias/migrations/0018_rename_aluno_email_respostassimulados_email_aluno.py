# Generated by Django 4.2.1 on 2023-05-26 23:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0017_respostassimulados_aluno_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='respostassimulados',
            old_name='aluno_email',
            new_name='email_aluno',
        ),
    ]
