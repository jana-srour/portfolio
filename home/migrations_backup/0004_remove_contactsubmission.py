from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_contactsubmission_delete_smtpconfig'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ContactSubmission',
        ),
    ]
