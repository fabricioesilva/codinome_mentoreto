# Generated by Django 4.2.1 on 2023-06-02 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0039_alter_simulados_gabarito'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorias',
            name='simulados_mentoria',
            field=models.ManyToManyField(blank=True, to='mentorias.simulados'),
        ),
    ]
