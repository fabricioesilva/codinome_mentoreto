# Generated by Django 4.2.1 on 2023-05-24 23:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0009_simulados_gabarito_simulados_pontuação'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulados',
            name='data_aplicacao',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Data prevista para aplicação'),
        ),
    ]
