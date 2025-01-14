from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import base58
# Create your models here.

class CustomUser(AbstractUser):
    user_id = models.UUIDField(verbose_name="user_id", default=uuid.uuid4, editable=False, primary_key=True)
    short_user_id = models.CharField(verbose_name="short_user_id", max_length=8, editable=False, unique=True)
    is_visible = models.BooleanField(verbose_name="is_visible", default=True)

    class Meta:
        db_table = "custom_user"

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.short_user_id:
            self.short_user_id = base58.b58encode(self.user_id.bytes).decode('utf-8')[:8]
        return super().save(*args, **kwargs)

class Collaboration(models.Model):
    request_id = models.UUIDField(verbose_name="request_id", default=uuid.uuid4, primary_key=True)
    from_user = models.ForeignKey(CustomUser, related_name="collaboration_from", on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name="collaboration_to", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "collaboration"
        unique_together = ("from_user", "to_user")
    
    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"
    

