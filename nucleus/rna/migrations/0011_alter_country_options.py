# Generated by Django 3.2.23 on 2023-11-23 13:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rna", "0010_note_only_applies_to_countries"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="country",
            options={"ordering": ["name"], "verbose_name_plural": "Countries"},
        ),
    ]