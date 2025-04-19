from django.http import JsonResponse, Http404
from .models import UserProfile, customer
from rest_framework.generics import GenericAPIView
from .serilalizers import CustomerRegisterSerializer, LoginSerializer, LogoutUserSerializer
from rest_framework import status
from rest_framework.permissions import  IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json 
from django.views.decorators.http import require_POST


class RegisterUserView(GenericAPIView):
    serializer_class = CustomerRegisterSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            return JsonResponse({
                'data': user,
                'message': f'hi {customer.First_Name} thanks for signing up a passcode'
            }, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return  JsonResponse(serializer.data, status=status.HTTP_200_OK)

class TestAuthenticationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            'msg': "Login Verified"
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Optionally validate token structure only
        refresh_token = serializer.validated_data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            # Don't blacklist — just acknowledge logout
            return JsonResponse({'message': 'Logout acknowledged. Please delete the token on client side.'}, status=status.HTTP_200_OK)
        except TokenError as e:
            return JsonResponse({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def customer_info(request, customer_id):
    customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)

    customer_data = {
        'First_Name': customer_obj.First_Name,
        'Last_Name': customer_obj.Last_Name,
        'Email': customer_obj.EMAIL,
    }
    return JsonResponse(customer_data)


@csrf_exempt
@require_POST
def edit_customer_info(request, customer_id):
    try:
        customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)
        data = json.loads(request.body.decode('utf-8'))

        if 'First_Name' in data:
            customer_obj.First_Name = data['First_Name']
        if 'Last_Name' in data:
            customer_obj.Last_Name = data['Last_Name']
        if 'Email' in data:
            customer_obj.EMAIL = data['Email']

        customer_obj.save()

        return JsonResponse({
            'message': 'Customer info updated successfully.',
            'data': {
                'First_Name': customer_obj.First_Name,
                'Last_Name': customer_obj.Last_Name,
                'Email': customer_obj.EMAIL,
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def change_customer_password(request, customer_id):
    try:
        data = json.loads(request.body.decode('utf-8'))
        new_password = data.get('new_password')

        if not new_password:
            return JsonResponse({'error': 'new_password is required.'}, status=400)

        # Get the customer by ID
        customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)

        # Set the new password securely
        customer_obj.set_password(new_password)
        customer_obj.save()

        return JsonResponse({'message': 'Password updated successfully.'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_POST
def recover_account(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        new_password = data.get('new_password', None)  # Optional on first step

        if not email:
            return JsonResponse({'error': 'Email is required.'}, status=400)

        customer_obj = customer.objects.filter(EMAIL=email).first()
        if not customer_obj:
            return JsonResponse({'error': 'Customer with this email does not exist.'}, status=404)

        # Step 1: Only email is provided
        if not new_password:
            return JsonResponse({'message': 'Email verified. Please provide a new password.'}, status=200)

        # Step 2: New password is provided
        customer_obj.set_password(new_password)
        customer_obj.save()

        return JsonResponse({'message': 'Password reset successfully.'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
