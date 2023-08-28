# Generated by Django 4.0 on 2023-08-27 23:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0026_delete_respostassimulados'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='descontos',
            name='criado_por',
        ),
        migrations.RemoveField(
            model_name='planosassinatura',
            name='criado_por',
        ),
        migrations.RemoveField(
            model_name='planosassinatura',
            name='desconto',
        ),
        migrations.RemoveField(
            model_name='alunos',
            name='simulados_realizados',
        ),
        migrations.DeleteModel(
            name='AssinaturasMentor',
        ),
        migrations.DeleteModel(
            name='Descontos',
        ),
        migrations.DeleteModel(
            name='PlanosAssinatura',
        ),
    ]
