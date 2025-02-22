# Generated by Django 4.2.1 on 2023-07-25 01:03

from django.db import migrations, models
import mentorias.models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0076_alter_mentoria_resumo_mentoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aplicacaosimulado',
            name='senha_do_aluno',
            field=models.TextField(blank=True, default=mentorias.models.get_random_string, null=True, verbose_name='Senha para acesso'),
        ),
        migrations.AlterField(
            model_name='aplicacaosimulado',
            name='simulado_titulo',
            field=models.TextField(blank=True, null=True, verbose_name='Titulo do simulado'),
        ),
    ]
