# Generated by Django 4.2.1 on 2023-07-15 21:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0014_alter_customuser_cnpj_faturamento_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preferences',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Preferências do usuário'),
        ),
    ]
