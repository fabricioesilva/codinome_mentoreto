# Generated by Django 4.2.3 on 2024-02-08 23:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0061_alter_loginalunos_criada_em_aluno_login_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginalunos',
            name='criada_em_aluno_login',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 8, 20, 8, 56, 438030), verbose_name='Criada em:'),
        ),
    ]
