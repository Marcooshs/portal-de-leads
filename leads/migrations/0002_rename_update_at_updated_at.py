from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="lead",
            old_name="update_at",
            new_name="updated_at",
        ),
    ]
