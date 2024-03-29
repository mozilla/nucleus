# Generated by Django 3.2.23 on 2023-11-23 13:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rna", "0009_data_bootstrap_countries_and_codes"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="relevant_countries",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Select the countries where this Note applies, as part of a "
                    "progressive rollout. This info will only be shown on the Release "
                    "page if 'Progressive rollout', above, is ticked."
                ),
                to="rna.Country",
            ),
        ),
    ]
