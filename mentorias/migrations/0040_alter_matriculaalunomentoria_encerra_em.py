# Generated by Django 4.2.3 on 2024-01-20 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0039_alter_mentoria_encerra_em'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matriculaalunomentoria',
            name='encerra_em',
            field=models.DateField(blank=True, null=True, verbose_name='Encerramento mentoria'),
        ),
    ]