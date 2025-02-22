# Generated by Django 4.2.1 on 2023-06-28 22:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0063_remove_aplicacaosimulado_respostas_alunos_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='aplicacaosimulado',
            name='matricula',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mentorias.matriculaalunomentoria'),
        ),
        migrations.AddField(
            model_name='matriculaalunomentoria',
            name='estatisticas',
            field=models.JSONField(blank=True, null=True, verbose_name='Estatísticas'),
        ),
    ]
