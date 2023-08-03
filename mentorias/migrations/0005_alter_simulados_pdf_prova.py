# Generated by Django 4.0 on 2023-08-02 23:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mentorias', '0004_arquivosmentoria_simulado_simulados_pdf_prova'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulados',
            name='pdf_prova',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pdf_prova', to='mentorias.arquivosmentoria'),
        ),
    ]
