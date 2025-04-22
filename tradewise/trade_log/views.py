from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import datetime
from upload_file.models import TransactionDetail
from .models import TradeLogs
import json


def update_trade_logs_for_customer_account(customer_id, account_id):
    unique_uploads = TransactionDetail.objects.filter(
        CUSTOMER_ID=customer_id,
        ACCOUNT_ID=account_id
    ).values('FILENAME', 'CREATE_DATE').distinct()

    logs_created = 0

    for upload in unique_uploads:
        filename = upload['FILENAME']
        create_date = upload['CREATE_DATE']

        if not TradeLogs.objects.filter(
            CUSTOMER_ID=customer_id,
            ACCOUNT_ID=account_id,
            FILE_NAME=filename,
            CREATE_DATE=create_date
        ).exists():
            TradeLogs.objects.create(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id,
                FILE_NAME=filename,
                UPLOAD_TIME=datetime.now(),
                TOTAL_ENTRIES=TransactionDetail.objects.filter(
                    CUSTOMER_ID=customer_id,
                    ACCOUNT_ID=account_id,
                    FILENAME=filename,
                    CREATE_DATE=create_date
                ).count(),
                DUPLICATE_ENTRIES=0,
                CREATE_DATE=create_date,
                CREATED_BY='system'
            )
            logs_created += 1

    return logs_created


@csrf_exempt
@require_POST
def log_uploaded_filenames(request):
    try:
        body = json.loads(request.body)
        customer_id = body.get('customer_id')
        account_id = body.get('account_id')

        if not customer_id or not account_id:
            return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

        logs_created = update_trade_logs_for_customer_account(customer_id, account_id)

        return JsonResponse({'message': f'{logs_created} trade logs created.'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_trade_logs_by_customer_account(request):
    try:
        body = json.loads(request.body)
        customer_id = body.get('customer_id')
        account_id = body.get('account_id')

        if not customer_id or not account_id:
            return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

        # Ensure logs are updated before fetching
        update_trade_logs_for_customer_account(customer_id, account_id)

        logs = TradeLogs.objects.filter(
            CUSTOMER_ID=customer_id,
            ACCOUNT_ID=account_id
        ).order_by('-UPLOAD_TIME')

        data = list(logs.values())

        return JsonResponse({'logs': data}, safe=False, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def get_trade_logs_by_date_range(request):
    try:
        body = json.loads(request.body)
        customer_id = body.get('customer_id')
        account_id = body.get('account_id')
        start_date = body.get('start_date')
        end_date = body.get('end_date')

        if not customer_id or not account_id or not start_date or not end_date:
            return JsonResponse({'error': 'customer_id, account_id, start_date, and end_date are required'}, status=400)

        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Ensure logs are updated before fetching
        update_trade_logs_for_customer_account(customer_id, account_id)

        logs = TradeLogs.objects.filter(
            CUSTOMER_ID=customer_id,
            ACCOUNT_ID=account_id,
            CREATE_DATE__range=(start_date_obj, end_date_obj)
        ).order_by('-UPLOAD_TIME')

        if not logs.exists():
            return JsonResponse({'message': 'No file uploaded.'}, status=200)

        data = list(logs.values())
        return JsonResponse({'logs': data}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
