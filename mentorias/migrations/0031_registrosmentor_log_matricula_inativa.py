# Generated by Django 4.0 on 2023-08-28 01:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0030_remove_matriculaalunomentoria_encerrada_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrosmentor',
            name='log_matricula_inativa',
            field=models.BooleanField(null=True, verbose_name='Inativa ou ativa'),
        ),
    ]
