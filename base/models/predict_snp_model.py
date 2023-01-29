from django.db import models


class PredictSNPJobModel(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        COMPLETED = "completed"
        FAILED = "failed"

    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    root_folder = models.CharField(max_length=60, default='Unknown')

    class Meta:
        db_table = 'predict_snp_jobs'
