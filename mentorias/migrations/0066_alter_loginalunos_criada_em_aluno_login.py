# Generated by Django 4.2.3 on 2024-02-13 16:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0065_alter_loginalunos_criada_em_aluno_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginalunos',
            name='criada_em_aluno_login',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 13, 16, 7, 4, 563206, tzinfo=datetime.timezone.utc), verbose_name='Criada em:'),
        ),
    ]