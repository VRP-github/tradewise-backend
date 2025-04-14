from django.shortcuts import render
from upload_file.models import TransactionSummary
from portfolio_organizer.models import PortfolioOrganizer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from datetime import date


@csrf_exempt
def fetch_account_names(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer_id')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not customer_id:
            return JsonResponse({'error': 'customer_id is required'}, status=400)

        accounts = PortfolioOrganizer.objects.filter(CUSTOMER_ID=customer_id).values('ACCOUNT_ID', 'ACCOUNT_NAME')
        account_list = list(accounts)

        return JsonResponse({'accounts': account_list}, status=200)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def update_transaction_commission_fees(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Extract and validate inputs
        customer_id = data.get('customer_id')
        account_id = data.get('account_id')
        commission = data.get('commission')
        fees = data.get('fees')

        if not all([customer_id, account_id, commission, fees]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Find matching records
        transactions = TransactionSummary.objects.filter(
            CUSTOMER_ID=customer_id,
            ACCOUNT_ID=account_id
        )

        if not transactions.exists():
            return JsonResponse({'message': 'No matching transactions found'}, status=404)

        # Update each transaction
        updated_count = transactions.update(
            COMMISSION=commission,
            FEES=fees
        )

        return JsonResponse({
            'message': f'Successfully updated {updated_count} transaction(s).'
        }, status=200)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
