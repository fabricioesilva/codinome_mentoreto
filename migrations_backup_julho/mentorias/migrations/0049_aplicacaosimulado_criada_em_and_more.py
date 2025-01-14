# Generated by Django 4.2.1 on 2023-06-06 00:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0048_alter_mentorias_simulados_mentoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='aplicacaosimulado',
            name='criada_em',
            field=models.DateField(default=datetime.date.today, verbose_name='Data'),
        ),
        migrations.AlterField(
            model_name='aplicacaosimulado',
            name='data_resposta',
            field=models.DateField(blank=True, null=True, verbose_name='Data da resposta'),
        ),
    ]
