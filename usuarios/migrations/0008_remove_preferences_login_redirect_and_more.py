# Generated by Django 4.2.1 on 2023-05-21 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_alter_useremailcheck_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preferences',
            name='login_redirect',
        ),
        migrations.AddField(
            model_name='preferences',
            name='Ferramenta favorita',
            field=models.SmallIntegerField(choices=[(1, 'Estudante'), (2, 'Mentor'), (3, 'Sempre perguntar')], default=3, verbose_name='Ir direto para o painel preferido ao iniciar sessão'),
        ),
    ]
