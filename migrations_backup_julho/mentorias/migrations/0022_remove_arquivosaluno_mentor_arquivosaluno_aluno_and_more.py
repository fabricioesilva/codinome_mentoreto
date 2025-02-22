# Generated by Django 4.2.1 on 2023-05-27 00:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mentorias', '0021_alter_respostassimulados_simulado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='arquivosaluno',
            name='mentor',
        ),
        migrations.AddField(
            model_name='arquivosaluno',
            name='aluno',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mentorias.alunos', verbose_name='Aluno'),
        ),
        migrations.AlterField(
            model_name='arquivosaluno',
            name='student_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
