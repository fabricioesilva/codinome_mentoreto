# Generated by Django 4.2.3 on 2024-02-05 01:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0050_registrosmentor_log_data_desativada_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAlunos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_aluno_login', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('senha_aluno_login', models.CharField(blank=True, max_length=6, null=True, verbose_name='Senha')),
                ('criada_em_aluno_login', models.DateTimeField(default=datetime.datetime(2024, 2, 4, 22, 13, 7, 39806), verbose_name='Criada em:')),
                ('nome_aluno_login', models.CharField(blank=True, max_length=100, null=True, verbose_name='Nome do Aluno')),
                ('telefone_aluno_login', models.CharField(blank=True, max_length=25, null=True, verbose_name='Telefone do Aluno')),
            ],
        ),
        migrations.AlterModelOptions(
            name='registrosmentor',
            options={'ordering': ['-pk']},
        ),
    ]
