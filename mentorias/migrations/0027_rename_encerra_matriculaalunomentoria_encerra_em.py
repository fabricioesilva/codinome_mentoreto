# Generated by Django 4.2.1 on 2023-05-27 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0026_matriculaalunomentoria_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matriculaalunomentoria',
            old_name='encerra',
            new_name='encerra_em',
        ),
    ]
