# Generated by Django 4.2.1 on 2023-05-24 23:39

import django.core.validators
from django.db import migrations, models
import mentorias.models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0010_alter_simulados_data_aplicacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='arquivosmentoria',
            name='arquivo_mentor',
            field=models.FileField(help_text='Insira arquivo em .pdf de até 5MB de tamanho.', null=True, upload_to=mentorias.models.user_directory_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf']), mentorias.models.file_size], verbose_name='Arquvio mentoria'),
        ),
        migrations.AddField(
            model_name='arquivosmentoria',
            name='mentor_nome',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Criado por:'),
        ),
        migrations.AddField(
            model_name='arquivosmentoria',
            name='titulo_arquivo',
            field=models.CharField(max_length=50, null=True, verbose_name='Nome do arquivo'),
        ),
    ]
