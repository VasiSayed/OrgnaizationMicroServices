# Generated by Django 5.2.3 on 2025-07-01 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_company_created_by_entity_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='organization',
            unique_together={('created_by', 'name')},
        ),
    ]
