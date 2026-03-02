from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json
import uuid
from rest_framework.decorators import api_view
from .models import PasswordReset
from django.http import HttpResponse
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import permission_classes


User = get_user_model()


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            return Response({
                "message": "Login successful",
                "full_name": user.full_name,
                "email": user.email
            })
        return Response(serializer.errors, status=400)

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)

        # ✅ CREATE TOKEN FIRST
        token = str(uuid.uuid4())

        # Save token in DB
        PasswordReset.objects.create(
            user=user,
            token=token
        )

        # Create reset link
        reset_link = f"http://localhost:8000/reset-password/{token}/"

        # Send email
        send_mail(
            "TourMate Password Reset",
            f"Click this link to reset your password:\n{reset_link}",
            "yourgmail@gmail.com",
            [email],
            fail_silently=False,
        )

        return Response({"message": "Reset link sent"}, status=200)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

def reset_password_page(request, token):
    if request.method == "GET":
        return render(request, "reset_form.html", {"token": token})

    if request.method == "POST":
        new_password = request.POST.get("new_password")

        try:
            reset = PasswordReset.objects.get(token=token)
            user = reset.user

            user.set_password(new_password)
            user.save()

            reset.delete()

            return HttpResponse("Password reset successful")

        except:
            return HttpResponse("Invalid or expired token")
        
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    serializer = ProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint - invalidates user token
    The frontend should delete the stored token after calling this endpoint
    """
    try:
        # With JWT, tokens are stateless so there's nothing to invalidate on backend
        # The frontend handles token deletion from local storage
        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"error": f"Logout failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

