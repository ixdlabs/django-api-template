from django.db import migrations, models


def populate_sn(apps, schema_editor):
    customer_enrollment_model = apps.get_model("users", "CustomerEnrollment")
    from collections import defaultdict

    branch_counters = defaultdict(int)

    # Assign incrementing SNs per branch
    for enrollment in customer_enrollment_model.objects.order_by("branch_id", "created"):
        branch_id = enrollment.branch_id
        branch_counters[branch_id] += 1
        enrollment.sn = branch_counters[branch_id]
        enrollment.save(update_fields=["sn"])


def populate_sn_reverse(apps, schema_editor):
    customer_enrollment_model = apps.get_model("users", "CustomerEnrollment")
    customer_enrollment_model.objects.all().update(sn=None)


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0004_branch_code_organization_code_and_more"),
        ("users", "0002_user_emp_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerenrollment",
            name="sn",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunPython(populate_sn, populate_sn_reverse),
        migrations.AlterField(
            model_name="customerenrollment",
            name="sn",
            field=models.PositiveIntegerField(null=False),
        ),
        migrations.AddConstraint(
            model_name="customerenrollment",
            constraint=models.UniqueConstraint(fields=("branch", "sn"), name="unique_branch_customer_sn"),
        ),
    ]
