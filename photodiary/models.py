from django.db import models
from django.conf import settings

class PhotoMemory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photo_memories"
    )
    image = models.ImageField(upload_to='photo_memories/')
    caption = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.caption}"


