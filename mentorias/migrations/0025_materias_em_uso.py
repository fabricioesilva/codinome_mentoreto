# Generated by Django 4.0 on 2023-08-24 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0024_alter_aplicacaosimulado_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='materias',
            name='em_uso',
            field=models.BooleanField(default=True, verbose_name='Em uso'),
        ),
    ]