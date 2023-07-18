# Generated by Django 4.2.1 on 2023-07-18 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0075_alter_aplicacaosimulado_senha_do_aluno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentoria',
            name='resumo_mentoria',
            field=models.TextField(blank=True, help_text='Se desejar, escreva um texto de apresentação desta mentoria ao estudante.', max_length=300, null=True, verbose_name='Apresentação da mentoria'),
        ),
    ]