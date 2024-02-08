# Generated by Django 4.2.3 on 2024-02-08 13:37

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0059_alter_loginalunos_criada_em_aluno_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginalunos',
            name='criada_em_aluno_login',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 8, 10, 37, 45, 851143), verbose_name='Criada em:'),
        ),
        migrations.AlterField(
            model_name='mentoria',
            name='encerra_em',
            field=models.DateField(blank=True, default=django.utils.timezone.now, help_text='Todas as matrículas desta mentoria durarão até no máximo esta data.', null=True, verbose_name='Fim da mentoria:'),
        ),
    ]
