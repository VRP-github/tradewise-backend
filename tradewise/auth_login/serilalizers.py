from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import update_last_login
from .models import customer
import logging
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
import traceback

api_settings.USER_ID_FIELD = "CUSTOMER_ID"

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()
#
#     def validate(self, data):
#         username = data.get('EMAIL', None)
#         password = data.get('password', None)
#         user = authenticate(username=username, password=password)
#         if user is None:
#             raise serializers.ValidationError('Invalid credentials')
#         return {'user': user}


class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=8, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=8, write_only=True)

    class Meta:
        model = customer
        fields = ['EMAIL', 'First_Name', 'Last_Name', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')

        if password != password2:
            raise serializers.ValidationError('Passwords does not match')

        return attrs

    def create(self, validate_data):
        Customer = customer.objects.create_user(
            EMAIL=validate_data.get('EMAIL'),
            First_Name=validate_data.get('First_Name'),
            Last_Name=validate_data.get('Last_Name'),
            password=validate_data.get('password'),
        )

        return Customer



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=100, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    customer_id = serializers.CharField(max_length=10, read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')

        # Authenticate user
        user = authenticate(request=request, username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid Credentials, Try Again!")
        logging.info(f"User authenticated successfully: {user.EMAIL}")

        # Update last login
        update_last_login(None, user)

        # Generate tokens
        tokens = user.tokens()

        return {
            'email': user.EMAIL,
            'full_name': f"{user.First_Name} {user.Last_Name}",
            'access_token': str(tokens.get('access')),
            'refresh_token': str(tokens.get('refresh')),
            'customer_id': user.CUSTOMER_ID,
        }



# class LogoutUserSerializer(serializers.Serializer):
#     refresh = serializers.CharField()

#     def validate(self, attrs):
#         # Ensure 'refresh' is present in the request data
#         if 'refresh' not in attrs:
#             raise serializers.ValidationError({'refresh': 'This field is required.'})

#         return attrs

#     def save(self, **kwargs):
#         refresh_token = self.validated_data['refresh']

#         try:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#         except Exception as e:
#             raise serializers.ValidationError({'error': str(e)})

class LogoutUserSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        if 'refresh' not in attrs:
            raise serializers.ValidationError({'refresh': 'This field is required.'})
        return attrs

    def save(self, **kwargs):
        # Just validate the token format but don't blacklist
        try:
            RefreshToken(self.validated_data['refresh'])
        except TokenError as e:
            raise serializers.ValidationError({'error': 'Invalid or expired token.'})
