# Generated by Django 4.0 on 2023-09-12 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assinaturas', '0010_remove_assinaturasmentor_log_meses_desconto_restante_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faturasmentores',
            name='desconto_aplicado',
        ),
        migrations.RemoveField(
            model_name='faturasmentores',
            name='quantidade_matriculas',
        ),
        migrations.RemoveField(
            model_name='faturasmentores',
            name='valor_total',
        ),
        migrations.AddField(
            model_name='faturasmentores',
            name='demonstrativo',
            field=models.JSONField(null=True, verbose_name='Demonstrativo das cobranças'),
        ),
    ]