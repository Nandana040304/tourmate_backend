from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PhotoMemory
from .serializers import PhotoMemorySerializer
from django.shortcuts import get_object_or_404
import os
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_photos(request):
    photos = PhotoMemory.objects.filter(user=request.user).order_by('-created_at')
    serializer = PhotoMemorySerializer(photos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_photo(request):
    serializer = PhotoMemorySerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    print(serializer.errors)  # VERY IMPORTANT
    return Response(serializer.errors, status=400)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_photo(request, photo_id):

    # 🔒 Make sure photo belongs to logged-in user
    photo = get_object_or_404(
        PhotoMemory,
        id=photo_id,
        user=request.user
    )

    # 🗑 Delete image file from media folder
    if photo.image:
        if os.path.isfile(photo.image.path):
            os.remove(photo.image.path)

    photo.delete()

    return Response(
        {"message": "Photo deleted successfully"},
        status=status.HTTP_200_OK
    )