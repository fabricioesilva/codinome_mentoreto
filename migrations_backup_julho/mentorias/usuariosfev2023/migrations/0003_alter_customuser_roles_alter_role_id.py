# Generated by Django 4.2.1 on 2023-05-20 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_useremailcheck_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='roles',
            field=models.ManyToManyField(blank=True, null=True, to='usuarios.role'),
        ),
        migrations.AlterField(
            model_name='role',
            name='id',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Estudante'), (2, 'Mentor'), (5, 'adm')], primary_key=True, serialize=False),
        ),
    ]