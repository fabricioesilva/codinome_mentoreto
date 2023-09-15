# Generated by Django 4.0 on 2023-08-28 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0031_registrosmentor_log_matricula_inativa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrosmentor',
            name='matricula',
        ),
        migrations.AlterField(
            model_name='matriculaalunomentoria',
            name='inativa',
            field=models.BooleanField(default=False, verbose_name='Está inativa'),
        ),
        migrations.AlterField(
            model_name='registrosmentor',
            name='log_matricula_inativa',
            field=models.BooleanField(null=True, verbose_name='Inativa'),
        ),
    ]