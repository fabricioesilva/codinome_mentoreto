# Generated by Django 4.2.1 on 2023-07-28 23:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0080_rename_aluno_do_arquivo_arquivosaluno_aluno_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='arquivosaluno',
            old_name='aluno',
            new_name='arquivos_do_aluno_aluno',
        ),
    ]
