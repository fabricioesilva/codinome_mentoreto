# Generated by Django 4.2.1 on 2023-06-07 02:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0050_alter_aplicacaosimulado_respostas_alunos'),
    ]

    operations = [
        migrations.AddField(
            model_name='aplicacaosimulado',
            name='aplicacao_agendada',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Agendar'),
        ),
    ]
