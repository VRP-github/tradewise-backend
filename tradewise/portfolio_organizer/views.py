from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import PortfolioOrganizer
from datetime import datetime
import json
import logging


@csrf_exempt
def insert_account(request, customer_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            account_name = data.get('Name')
            stock_type = data.get('Stock_Type')
            profit_calculation_method = data.get('Profit_Calculation_Method')
            balance = data.get('Balance')
            description = data.get('Description')
            status = data.get('status')
            created_by = data.get('Created_By')

            if not all([account_name, stock_type, profit_calculation_method, balance, description, created_by]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            initial_deposit = balance
            is_active = 'Y' if status else 'N'

            now = datetime.now()
            balance_date_obj = now.date()
            balance_time_obj = now.time()

            account = PortfolioOrganizer(
                CUSTOMER_ID=customer_id,
                ACCOUNT_NAME=account_name,
                STOCK_TYPE=stock_type,
                INITIAL_DEPOSIT=initial_deposit,
                IS_ACTIVE=is_active,
                CREATE_DATE=now.date(),
                CREATED_BY=created_by,
                LAST_UPDATED_DATE=now.date(),
                LAST_UPDATED_BY=created_by,
                PROFIT_CALCULATION_METHOD=profit_calculation_method,
                BALANCE_DATE=balance_date_obj,
                BALANCE_TIME=balance_time_obj,
                BALANCE_DESCRIPTION=description
            )
            account.save()

            return JsonResponse({'status': 'success', 'message': 'Account created successfully'}, status=201)

        except Exception as e:
            logging.error(f'Error inserting account: {str(e)}')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_active_portfolio_accounts(request, customer_id):
    try:
        active_accounts = PortfolioOrganizer.objects.filter(CUSTOMER_ID=customer_id, IS_ACTIVE='Y')
        accounts_data = []

        for account in active_accounts:
            accounts_data.append({
                'ACCOUNT_ID': account.ACCOUNT_ID,
                'CUSTOMER_ID': account.CUSTOMER_ID,
                'ACCOUNT_NAME': account.ACCOUNT_NAME,
                'STOCK_TYPE': account.STOCK_TYPE,
                'INITIAL_DEPOSIT': account.INITIAL_DEPOSIT,
                'IS_ACTIVE': account.IS_ACTIVE,
                'CREATE_DATE': account.CREATE_DATE,
                'CREATED_BY': account.CREATED_BY,
                'LAST_UPDATED_DATE': account.LAST_UPDATED_DATE,
                'LAST_UPDATED_BY': account.LAST_UPDATED_BY,
                'PROFIT_CALCULATION_METHOD': account.PROFIT_CALCULATION_METHOD,
                'BALANCE_DATE': account.BALANCE_DATE,
                'BALANCE_TIME': account.BALANCE_TIME,
                'BALANCE_DESCRIPTION': account.BALANCE_DESCRIPTION,
            })

        logging.info({'portfolio_accounts': accounts_data})
        return JsonResponse({'portfolio_accounts': accounts_data}, status=200)

    except PortfolioOrganizer.DoesNotExist:
        return JsonResponse({'error': 'No active portfolio accounts found for the customer'}, status=404)

    except Exception as e:
        logging.error({'error': str(e)})
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def update_portfolio_account(request, account_id):
    try:
        print(f"Account ID received: {account_id}")
        account = PortfolioOrganizer.objects.get(ACCOUNT_ID=account_id)

        data = json.loads(request.body.decode('utf-8'))

        if 'fields_to_update' in data:
            fields_to_update = data['fields_to_update']
            
            if 'name' in fields_to_update:
                account.ACCOUNT_NAME = fields_to_update['name']
            if 'stock_type' in fields_to_update:
                account.STOCK_TYPE = fields_to_update['stock_type']
            if 'profit_calculation_method' in fields_to_update:
                account.PROFIT_CALCULATION_METHOD = fields_to_update['profit_calculation_method']
            if 'balance' in fields_to_update:
                account.INITIAL_DEPOSIT = fields_to_update['balance']
           
            account.LAST_UPDATED_DATE = datetime.now().date()

            account.save()

            logging.info({'message': f'Portfolio account {account_id} updated successfully'})
            return JsonResponse({'message': f'Portfolio account {account_id} updated successfully'}, status=200)
        else:
            logging.error({'error': 'No data provided for update'})
            return JsonResponse({'error': 'No data provided for update'}, status=400)

    except PortfolioOrganizer.DoesNotExist:
        logging.error({'error': f'Portfolio account with id {account_id} does not exist'})
        return JsonResponse({'error': f'Portfolio account with id {account_id} does not exist'}, status=404)

    except Exception as e:
        logging.error({'error': str(e)})
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def delete_portfolio_account(request, customer_id, account_id):
    try:
        account = PortfolioOrganizer.objects.get(CUSTOMER_ID=customer_id, ACCOUNT_ID=account_id)

        account.IS_ACTIVE = 'N'
        account.save()

        logging.info({'message': f'Portfolio account {account_id} deleted successfully'})
        return JsonResponse({'message': f'Portfolio account {account_id} deleted successfully'}, status=200)

    except PortfolioOrganizer.DoesNotExist:
        logging.error({'error': 'Portfolio account not found'})
        return JsonResponse({'error': 'Portfolio account not found'}, status=404)

    except Exception as e:
        logging.error({'error': str(e)})
        return JsonResponse({'error': str(e)}, status=500)
