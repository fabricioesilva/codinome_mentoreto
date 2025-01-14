# Generated by Django 4.2.3 on 2024-02-05 13:59

import datetime
from django.db import migrations, models
import mentorias.models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0053_alter_loginalunos_criada_em_aluno_login_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginalunos',
            name='criada_em_aluno_login',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 5, 10, 59, 16, 469673), verbose_name='Criada em:'),
        ),
        migrations.AlterField(
            model_name='loginalunos',
            name='senha_aluno_login',
            field=models.CharField(blank=True, default=mentorias.models.get_random_string, max_length=8, null=True, verbose_name='Senha'),
        ),
    ]
