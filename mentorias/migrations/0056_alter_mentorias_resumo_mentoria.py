# Generated by Django 4.2.1 on 2023-06-08 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0055_alter_alunos_situacao_aluno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentorias',
            name='resumo_mentoria',
            field=models.TextField(blank=True, max_length=300, null=True, verbose_name='Resumo'),
        ),
    ]
