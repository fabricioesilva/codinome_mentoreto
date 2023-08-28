# Generated by Django 4.0 on 2023-08-28 00:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0028_matriculaalunomentoria_encerrada_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alunos',
            name='criado_em',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data do cadastramento do aluno'),
        ),
        migrations.AlterField(
            model_name='matriculaalunomentoria',
            name='criada_em',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data da matrícula'),
        ),
        migrations.AlterField(
            model_name='mentoria',
            name='criada_em',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Data criação:'),
        ),
    ]
