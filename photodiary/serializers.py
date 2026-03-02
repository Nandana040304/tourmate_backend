from rest_framework import serializers
from .models import PhotoMemory

class PhotoMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoMemory
        fields = ['id', 'image', 'caption', 'location', 'created_at']