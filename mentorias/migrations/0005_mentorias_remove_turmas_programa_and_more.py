# Generated by Django 4.2.1 on 2023-05-24 00:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mentorias', '0004_alter_programas_arquivos_programa'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mentorias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(help_text='Insira um título para a mentoria.', max_length=100, verbose_name='Titulo da mentoria')),
                ('created', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Data criação:')),
                ('controle', models.TextField(blank=True, help_text='Anotações da Mentoria para seu controle. Apenas você terá acesso a este conteúdo.', null=True, verbose_name='Anotações da mentoria')),
                ('etapas', models.JSONField(blank=True, null=True, verbose_name='Etapas da mentoria')),
            ],
        ),
        migrations.RemoveField(
            model_name='turmas',
            name='programa',
        ),
        migrations.AlterField(
            model_name='turmas',
            name='descricao',
            field=models.CharField(blank=True, help_text='Inclua uma descrição resumida da Turma, que fica disponível para o estudante.', max_length=100, null=True, verbose_name='Descrição da mentoria'),
        ),
        migrations.RenameModel(
            old_name='ArquivosPrograma',
            new_name='ArquivosMentoria',
        ),
        migrations.DeleteModel(
            name='Programas',
        ),
        migrations.AddField(
            model_name='mentorias',
            name='arquivos_mentoria',
            field=models.ManyToManyField(blank=True, help_text='Arquivos de uma mentoria são arquivos disponíveis aos estudantes                 que fizerem parte da mentoria.', to='mentorias.arquivosmentoria'),
        ),
        migrations.AddField(
            model_name='mentorias',
            name='mentor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='turmas',
            name='mentoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mentorias.mentorias'),
        ),
    ]
