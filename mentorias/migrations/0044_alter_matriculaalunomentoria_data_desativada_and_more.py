# Generated by Django 4.2.3 on 2024-01-21 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0043_matriculaalunomentoria_data_reativada_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matriculaalunomentoria',
            name='data_desativada',
            field=models.DateField(blank=True, null=True, verbose_name='Data e hora em que foi desativada'),
        ),
        migrations.AlterField(
            model_name='matriculaalunomentoria',
            name='data_reativada',
            field=models.DateField(blank=True, null=True, verbose_name='Data e hora em que foi reativada'),
        ),
    ]
