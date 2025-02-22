# Generated by Django 4.2.3 on 2024-02-07 23:06

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assinaturas', '0036_remove_termosaceitos_login_aluno_and_more'),
        ('mentorias', '0056_alter_loginalunos_criada_em_aluno_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loginalunos',
            name='criada_em_aluno_login',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 7, 20, 6, 7, 948760), verbose_name='Criada em:'),
        ),
        migrations.CreateModel(
            name='TermosAceitosAluno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.EmailField(max_length=254, verbose_name='Email do usuário')),
                ('profile_id', models.IntegerField(verbose_name='Id do usuário')),
                ('acept_date', models.DateTimeField(auto_now_add=True, verbose_name='Data da aceitação')),
                ('login_aluno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mentorias.loginalunos', verbose_name='Login do aluno')),
                ('termo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assinaturas.termosdeuso', verbose_name='Termos de Uso')),
            ],
        ),
    ]
