# Generated by Django 4.2.16 on 2025-02-17 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projetoApp', '0005_instituicao_participante_instituicao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participante',
            name='instituicao',
        ),
        migrations.AddField(
            model_name='instituicao',
            name='participantes',
            field=models.ManyToManyField(to='projetoApp.participante', verbose_name='Participantes'),
        ),
    ]
