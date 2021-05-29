from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from .mail import send_reset_email
from .serializers import UserSerializer
from django.utils import timezone
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode


User = get_user_model()


@api_view(http_method_names=["POST"])
@permission_classes([])
@authentication_classes([])
def register(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(request.data["password"])
        user.save()

        token = Token.objects.create(user=user)

        data = {
            "user": UserSerializer(user).data,
            "token": token.key
        }

        return Response(status=201, data=data)


class LoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        return Response(status=200, data={
            'token': token.key,
            'user': UserSerializer(user).data
        })


@api_view(http_method_names=["POST"])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=200, data={"success": True})


@api_view(http_method_names=["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_user(request):
    data = UserSerializer(request.user).data
    return Response(status=200, data=data)


@api_view(http_method_names=["GET"])
@permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def get_all_users(request):
    data = UserSerializer(request.user).data
    return Response(status=200, data=data)


@api_view(http_method_names=["PUT", "PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_user(request):
    """Update user first_name, last_name, email"""
    user = request.user

    # Explicit is better than implicit
    if request.data.get("first_name"):
        user.first_name = request.data.get("first_name")

    if request.data.get("last_name"):
        user.last_name = request.data.get("last_name")

    if request.data.get("email"):
        user.email = request.data.get("email")

    user.save()

    serializer = UserSerializer(instance=user)
    return Response(status=200, data=serializer.data)


@api_view(http_method_names=["POST"])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password!"""
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password:
        raise serializers.ValidationError(
            {"old_password": ["old_password is required"]})

    if not new_password:
        raise serializers.ValidationError(
            {"new_password": ["new_password is required"]})

    user = authenticate(username=request.user.username, password=old_password)

    if not user:
        raise serializers.ValidationError(
            {"old_password": ["old_password is invalid!"]})

    user.set_password(new_password)
    user.save()

    return Response(status=200, data=UserSerializer(user).data)


@api_view(http_method_names=["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """
    Sends a password reset email that expires in 30 minutes.
    """

    email = request.data.get("email")
    user = get_object_or_404(User, email=email)
    subject = request.data.get("subject", "Password Reset email")

    try:
        sent = send_reset_email(request, user, subject)
        if sent:
            return Response(status=200, data={"message": "Password reset email sent successfully!"})
        else:
            return Response(status=400, data={"message": "Unable to send email!"})
    except Exception as e:
        return Response(status=500, data={"message": "Internal server error"})


@api_view(http_method_names=["POST", "GET"])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
def reset_password_confirmation(request, uidb64, token):
    user = get_user_from_base64(uidb64)

    if request.method == 'POST':
        # Post request to change password

        if not user:
            return Response(status=404, data={"error": "Invalidate user token!"})

        password = request.data.get("password", "")

        if len(password) < 8:
            raise serializers.ValidationError(
                "Password should be at least 8 characters")

        if PasswordResetTokenGenerator().check_token(user, token):
            user.set_password(password)
            user.last_login = timezone.localtime()
            user.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "user": UserSerializer(user).data,
                "token": token.key,
            })

        return Response(status=403, data={"message": "Password reset token has expired!"})
    else:
        # GET Requests when user click email link
        if not user:
            return HttpResponse("Invalid password reset token!")

        context = {
            "user": user,
            "site_name": settings.DRF_AUTH_SETTINGS["SITE_NAME"]
        }

        return render(request, "drf_auth/password_change_form.html", context=context)


def get_user_from_base64(uidb64):
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        user = None

    return user
