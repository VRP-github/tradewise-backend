from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models import CustomerProfile, TradeSetting
from auth_login.models import customer

@csrf_exempt
@require_POST
def create_customer_profile(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        customer_id = data.get('customer_id')
        timezone = data.get('timezone')
        currency = data.get('currency')

        if not (customer_id and timezone and currency):
            return JsonResponse({'error': 'customer_id, timezone, and currency are required.'}, status=400)

        customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)

        profile = CustomerProfile(
            customer_id=customer_obj,
            timezone=timezone,
            currency=currency
        )
        profile.save()

        return JsonResponse({
            'message': 'Customer profile created successfully.',
            'profile_id': profile.profile_id,
            'customer_id': customer_id,
            'timezone': profile.timezone,
            'currency': profile.currency,
            'is_active': profile.is_active
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def edit_customer_profile_by_customer_id(request, customer_id):
    try:
        print("Raw Body:", request.body)
        print("Content-Type:", request.META.get("CONTENT_TYPE"))

        if request.method != "POST":
            return JsonResponse({'error': 'Only POST method allowed'}, status=405)

        # Attempt to parse JSON
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            print("JSON decode error:", str(e))
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        # Fetch and update
        profile = get_object_or_404(CustomerProfile, customer_id__CUSTOMER_ID=customer_id)

        if 'timezone' in data:
            profile.timezone = data['timezone']
        if 'currency' in data:
            profile.currency = data['currency']
        if 'is_active' in data:
            profile.is_active = data['is_active']

        profile.save()

        return JsonResponse({
            'message': 'Customer profile updated successfully.',
            'profile_id': profile.profile_id,
            'customer_id': profile.customer_id.CUSTOMER_ID,
            'timezone': profile.timezone,
            'currency': profile.currency,
            'is_active': profile.is_active
        }, status=200)

    except Exception as e:
        print("Unhandled exception:", str(e))
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_customer_profiles_by_customer_id(request, customer_id):
    if request.method != "GET":
        return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)

    try:
        # Validate customer exists
        customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)

        # Get profiles linked to the customer
        profiles = CustomerProfile.objects.filter(customer_id=customer_obj)

        if not profiles.exists():
            return JsonResponse({'profiles': []}, status=200)

        profile_data = [
            {
                'profile_id': profile.profile_id,
                'timezone': profile.timezone,
                'currency': profile.currency,
                'is_active': profile.is_active,
            } for profile in profiles
        ]

        return JsonResponse({'profiles': profile_data}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_POST
def create_trade_setting(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        customer_id = data.get('customer_id')
        account_id = data.get('account_id')
        type_value = data.get('type')
        from_value = data.get('from_field')
        to_value = data.get('to_field')

        if not all([customer_id, account_id, type_value, from_value, to_value]):
            return JsonResponse({'error': 'All fields (customer_id, account_id, type, from_field, to_field) are required.'}, status=400)

        customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)

        trade_setting = TradeSetting.objects.create(
            customer_id=customer_obj,
            account_id=account_id,
            type=type_value,
            from_field=from_value,
            to_field=to_value
        )

        return JsonResponse({
            'message': 'Trade setting created successfully.',
            'data': {
                'trade_id': trade_setting.trade_id,
                'customer_id': customer_id,
                'account_id': account_id,
                'type': type_value,
                'from': from_value,
                'to': to_value
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_POST
def edit_trade_setting(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        customer_id = data.get('customer_id')
        if not customer_id:
            return JsonResponse({'error': 'customer_id is required in the request body.'}, status=400)

        # Fetch customer and related trade setting
        customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)
        trade_setting = get_object_or_404(TradeSetting, customer_id=customer_obj)

        # Track update status
        updated = False

        if 'type' in data:
            trade_setting.type = data['type']
            updated = True
        if 'from_field' in data:
            trade_setting.from_field = data['from_field']
            updated = True
        if 'to_field' in data:
            trade_setting.to_field = data['to_field']
            updated = True

        if not updated:
            return JsonResponse({
                'error': 'At least one of type, from_field, or to_field must be provided.'
            }, status=400)

        trade_setting.save()

        return JsonResponse({
            'message': 'Trade setting updated successfully.',
            'data': {
                'trade_id': trade_setting.trade_id,
                'customer_id': trade_setting.customer_id.CUSTOMER_ID,
                'account_id': trade_setting.account_id,
                'type': trade_setting.type,
                'from': trade_setting.from_field,
                'to': trade_setting.to_field
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_POST
def get_trade_setting_by_customer_and_account(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        customer_id = data.get('customer_id')
        account_id = data.get('account_id')

        if not customer_id or not account_id:
            return JsonResponse({'error': 'Both customer_id and account_id are required.'}, status=400)

        # Fetch customer and trade setting
        customer_obj = get_object_or_404(customer, CUSTOMER_ID=customer_id)
        trade_setting = get_object_or_404(TradeSetting, customer_id=customer_obj, account_id=account_id)

        return JsonResponse({
            'trade_id': trade_setting.trade_id,
            'customer_id': trade_setting.customer_id.CUSTOMER_ID,
            'account_id': trade_setting.account_id,
            'type': trade_setting.type,
            'from': trade_setting.from_field,
            'to': trade_setting.to_field
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



