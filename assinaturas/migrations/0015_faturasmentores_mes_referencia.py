# Generated by Django 4.0 on 2023-09-12 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assinaturas', '0014_faturasmentores_gastos_no_mes'),
    ]

    operations = [
        migrations.AddField(
            model_name='faturasmentores',
            name='mes_referencia',
            field=models.CharField(max_length=10, null=True, verbose_name='Mês de referência da fatura'),
        ),
    ]
