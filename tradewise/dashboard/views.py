from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from upload_file.models import TransactionSummary, TransactionDetail
import json

@csrf_exempt 
def total_profit_loss(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            customer_id = data.get('customer_id')
            account_id = data.get('account_id')

            if not customer_id or not account_id:
                return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

            transactions = TransactionSummary.objects.filter(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id
            )

            total = 0.0
            for txn in transactions:
                try:
                    total += float(txn.PROFIT_LOSS)
                except (ValueError, TypeError):
                    continue  

            return JsonResponse({
                'customer_id': customer_id,
                'account_id': account_id,
                'total_profit_loss': round(total, 2)
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def calculate_profit_percentage(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            customer_id = data.get('customer_id')
            account_id = data.get('account_id')

            if not customer_id or not account_id:
                return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

            transactions = TransactionSummary.objects.filter(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id
            )

            total_profit = 0.0
            total_buy_value = 0.0

            for txn in transactions:
                try:
                    profit = float(txn.PROFIT_LOSS)
                    avg_buy_price = float(txn.AVG_BUY_PRICE)
                    quantity = float(txn.QUANTITY)

                    total_profit += profit
                    total_buy_value += avg_buy_price * quantity
                except (ValueError, TypeError):
                    continue

            if total_buy_value == 0:
                return JsonResponse({
                    'customer_id': customer_id,
                    'account_id': account_id,
                    'profit_percentage': None,
                    'message': 'Total buy value is zero or invalid, cannot calculate percentage'
                }, status=400)

            profit_percent = (total_profit / total_buy_value) * 100

            return JsonResponse({
                'customer_id': customer_id,
                'account_id': account_id,
                'profit_percentage': round(profit_percent, 2)
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def calculate_profit_factor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            customer_id = data.get('customer_id')
            account_id = data.get('account_id')

            if not customer_id or not account_id:
                return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

            transactions = TransactionSummary.objects.filter(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id
            )

            gross_profit = 0.0
            gross_loss = 0.0

            for txn in transactions:
                try:
                    profit_loss = float(txn.PROFIT_LOSS)
                    if profit_loss >= 0:
                        gross_profit += profit_loss
                    else:
                        gross_loss += abs(profit_loss)
                except (ValueError, TypeError):
                    continue

            if gross_loss == 0:
                return JsonResponse({
                    'customer_id': customer_id,
                    'account_id': account_id,
                    'profit_factor': None,
                    'message': 'No losses recorded. Profit factor is undefined (division by zero).'
                }, status=400)

            profit_factor = gross_profit / gross_loss

            return JsonResponse({
                'customer_id': customer_id,
                'account_id': account_id,
                'profit_factor': round(profit_factor, 2)
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def calculate_avg_win_loss_ratio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            customer_id = data.get('customer_id')
            account_id = data.get('account_id')

            if not customer_id or not account_id:
                return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

            transactions = TransactionSummary.objects.filter(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id
            )

            total_win = 0.0
            win_count = 0
            total_loss = 0.0
            loss_count = 0

            for txn in transactions:
                try:
                    pl = float(txn.PROFIT_LOSS)
                    if pl > 0:
                        total_win += pl
                        win_count += 1
                    elif pl < 0:
                        total_loss += abs(pl)
                        loss_count += 1
                except (ValueError, TypeError):
                    continue

            if win_count == 0 or loss_count == 0:
                return JsonResponse({
                    'customer_id': customer_id,
                    'account_id': account_id,
                    'avg_win_loss_ratio': None,
                    'message': 'Insufficient data — need at least one win and one loss to calculate ratio.'
                }, status=400)

            avg_win = total_win / win_count
            avg_loss = total_loss / loss_count

            ratio = avg_win / avg_loss

            return JsonResponse({
                'customer_id': customer_id,
                'account_id': account_id,
                'avg_win_loss_ratio': round(ratio, 2)
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

@csrf_exempt
def get_zero_quantity_transactions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            customer_id = data.get('customer_id')
            account_id = data.get('account_id')

            if not customer_id or not account_id:
                return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

            zero_qty_txns = TransactionSummary.objects.filter(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id,
                QUANTITY=0
            )

            results = []
            for txn in zero_qty_txns:
                results.append({
                    'end_date': txn.TRADE_END_TIME,
                    'ticker': txn.TICKER,
                    'profit_loss': txn.PROFIT_LOSS
                })

            return JsonResponse({
                'customer_id': customer_id,
                'account_id': account_id,
                'transactions': results
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)



@csrf_exempt
def get_transaction_details(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            customer_id = data.get('customer_id')
            account_id = data.get('account_id')

            if not customer_id or not account_id:
                return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

            transactions = TransactionDetail.objects.filter(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id
            )

            results = []
            for txn in transactions:
                results.append({
                    'transaction_id': txn.TRANSACTION_DETAIL_ID,
                    'transaction_date': txn.TRANSACTION_DATE,
                    'type': txn.TYPE,
                    'ticker': txn.TICKER,
                    'identifier': txn.IDENTIFIER,
                    'quantity': txn.QUANTITY,
                    'order_type': txn.ORDER_TYPE,
                    'price': txn.PRICE,
                })

            return JsonResponse({
                'customer_id': customer_id,
                'account_id': account_id,
                'transaction_details': results
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)