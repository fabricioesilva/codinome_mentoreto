# Generated by Django 4.2.3 on 2024-02-22 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('politicas', '0008_policyrules_arquivo_politica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policyrules',
            name='title',
            field=models.CharField(max_length=50, null=True, verbose_name='Título da política'),
        ),
    ]