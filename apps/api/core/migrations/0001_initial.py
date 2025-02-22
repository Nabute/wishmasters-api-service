# Generated by Django 5.1.3 on 2025-02-21 16:53

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataLookup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='uuid')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='deleted at')),
                ('type', models.CharField(max_length=256, verbose_name='type')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('category', models.CharField(blank=True, max_length=256, null=True, verbose_name='category')),
                ('note', models.TextField(blank=True, null=True, verbose_name='note')),
                ('index', models.PositiveIntegerField(default=0, verbose_name='index')),
                ('is_default', models.BooleanField(default=False, verbose_name='is default')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='remark')),
            ],
            options={
                'verbose_name': 'data lookup',
                'verbose_name_plural': 'data lookups',
                'db_table': 'data_lookups',
                'constraints': [models.UniqueConstraint(condition=models.Q(('is_default', True)), fields=('type', 'is_default'), name='data_lookups_type_is_default_idx'), models.UniqueConstraint(fields=('type', 'index'), name='data_lookups_type_index_idx'), models.UniqueConstraint(fields=('value',), name='data_lookups_value_idx')],
            },
        ),
        migrations.CreateModel(
            name='SystemSetting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='uuid')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='deleted at')),
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('key', models.CharField(max_length=256, verbose_name='key')),
                ('default_value', models.CharField(max_length=256, verbose_name='default_value')),
                ('current_value', models.CharField(max_length=256, verbose_name='current_value')),
                ('data_scheme', models.TextField(blank=True, null=True, verbose_name='data_scheme')),
            ],
            options={
                'verbose_name': 'system setting',
                'verbose_name_plural': 'system settings',
                'db_table': 'system_settings',
                'constraints': [models.UniqueConstraint(fields=('key',), name='system_settings_key_idx')],
            },
        ),
    ]
