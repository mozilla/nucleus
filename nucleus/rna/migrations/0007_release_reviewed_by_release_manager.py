# Generated by Django 3.2.23 on 2023-11-20 22:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rna", "0006_note_progressive_rollout"),
    ]

    operations = [
        migrations.AddField(
            model_name="release",
            name="reviewed_by_release_manager",
            field=models.BooleanField(default=False, help_text="Purely a visual indicator in Nucleus - does not show on mozilla.org", null=True),
        ),
    ]
