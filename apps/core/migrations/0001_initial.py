# Generated by Django 3.2.8 on 2021-12-01 23:04

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HairCut',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('description', models.CharField(max_length=255, null=True, unique=True, verbose_name='description')),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=22, verbose_name='price')),
                ('minutes', models.PositiveIntegerField(default=10, verbose_name='minutes')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
            ],
            options={
                'verbose_name': 'haircut',
                'verbose_name_plural': 'haircuts',
            },
        ),
    ]