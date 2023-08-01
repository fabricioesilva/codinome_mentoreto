# Generated by Django 4.0 on 2023-08-01 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0002_auto_20230728_2345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alunos',
            name='arquivos_aluno',
            field=models.ManyToManyField(blank=True, help_text='Arquivos de um Aluno são arquivos disponíveis ao estudante selecionado.', to='mentorias.ArquivosDoAluno'),
        ),
        migrations.AlterField(
            model_name='alunos',
            name='simulados_realizados',
            field=models.ManyToManyField(blank=True, help_text='Simulados que os alunos devem fazer.', to='mentorias.Simulados'),
        ),
        migrations.AlterField(
            model_name='mentoria',
            name='arquivos_da_mentoria',
            field=models.ManyToManyField(blank=True, help_text='Arquivos de uma mentoria são arquivos disponíveis aos estudantes \t\t\t\tque fizerem parte da mentoria.', related_name='arquivos_da_mentoria', to='mentorias.ArquivosMentoria'),
        ),
        migrations.AlterField(
            model_name='mentoria',
            name='links_externos',
            field=models.ManyToManyField(blank=True, to='mentorias.LinksExternos'),
        ),
        migrations.AlterField(
            model_name='mentoria',
            name='matriculas',
            field=models.ManyToManyField(blank=True, to='mentorias.MatriculaAlunoMentoria'),
        ),
        migrations.AlterField(
            model_name='mentoria',
            name='simulados_mentoria',
            field=models.ManyToManyField(blank=True, to='mentorias.AplicacaoSimulado'),
        ),
        migrations.AlterField(
            model_name='planosassinatura',
            name='desconto',
            field=models.ManyToManyField(to='mentorias.Descontos'),
        ),
    ]
