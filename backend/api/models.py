from django.db import models
from django.utils import timezone


def upload_to(instance, filename: str) -> str:
    ts = timezone.now().strftime("%Y%m%dT%H%M%S")
    return f"uploads/{ts}_{filename}"


class UploadedDataset(models.Model):
    file = models.FileField(upload_to=upload_to)
    original_name = models.CharField(max_length=255)
    extension = models.CharField(max_length=16, blank=True, default="")
    columns = models.JSONField(default=list, blank=True)
    row_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.original_name} ({self.row_count} rows)"


class Transformation(models.Model):
    dataset = models.ForeignKey(UploadedDataset, on_delete=models.CASCADE, related_name="transforms")
    natural_language = models.TextField()
    pattern = models.TextField()
    replacement = models.TextField(blank=True, default="")
    target_columns = models.JSONField(default=list, blank=True)

    apply_phone_normalization = models.BooleanField(default=False)
    apply_date_normalization = models.BooleanField(default=False)

    result_preview = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Transform on {self.dataset_id} @ {self.created_at:%Y-%m-%d %H:%M:%S}"
