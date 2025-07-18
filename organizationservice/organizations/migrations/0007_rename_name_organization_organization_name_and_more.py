# Generated by Django 5.2.3 on 2025-07-01 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0006_alter_organization_unique_together'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organization',
            old_name='name',
            new_name='organization_name',
        ),
        migrations.AlterUniqueTogether(
            name='organization',
            unique_together={('created_by', 'organization_name')},
        ),
    ]
