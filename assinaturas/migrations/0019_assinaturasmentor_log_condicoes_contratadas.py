# Generated by Django 4.0 on 2023-09-15 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assinaturas', '0018_precosassinatura_condicoes'),
    ]

    operations = [
        migrations.AddField(
            model_name='assinaturasmentor',
            name='log_condicoes_contratadas',
            field=models.TextField(blank=True, null=True, verbose_name='Condições do plano em HTML'),
        ),
    ]
