# Generated by Django 4.2.1 on 2023-07-16 23:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0072_alter_aplicacaosimulado_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='aplicacaosimulado',
            unique_together={('aluno', 'simulado_titulo')},
        ),
    ]
