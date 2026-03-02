
from django.urls import path
from .views import get_user_photos, upload_photo, delete_photo

urlpatterns = [
    path('my-photos/', get_user_photos),
    path('upload/', upload_photo),
    path('delete/<int:photo_id>/', delete_photo),
]
