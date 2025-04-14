import json
from portfolio_organizer.models import PortfolioOrganizer
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from upload_file.models import TransactionSummary
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

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
def fetch_account_symbols(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer_id')
            account_id = data.get('account_id')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    elif request.method == 'GET':
        customer_id = request.GET.get('customer_id')
        account_id = request.GET.get('account_id')

    else:
        return JsonResponse({'error': 'Unsupported request method'}, status=405)

    if not customer_id or not account_id:
        return JsonResponse({'error': 'customer_id and account_id are required'}, status=400)

    tickers = (
        TransactionSummary.objects
        .filter(CUSTOMER_ID=customer_id, ACCOUNT_ID=account_id)
        .values_list('TICKER', flat=True)
        .distinct()
    )
    ticker_list = list(tickers)

    return JsonResponse({'tickers': ticker_list}, status=200)

    
@csrf_exempt
def fetch_download_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    elif request.method == 'GET':
        data = request.GET
    else:
        return JsonResponse({'error': 'Only GET and POST methods are allowed'}, status=405)

    customer_id = data.get('customer_id')
    account_id = data.get('account_id')
    ticker = data.get('ticker')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    file_type = data.get('file_type', 'xlsx').lower()

    if not all([customer_id, account_id, ticker, start_date, end_date]):
        return JsonResponse({'error': 'customer_id, account_id, ticker, start_date, and end_date are required'}, status=400)

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    transactions = TransactionSummary.objects.filter(
        CUSTOMER_ID=customer_id,
        ACCOUNT_ID=account_id,
        TICKER=ticker,
        TRANSACTION_DATE__range=(start_date, end_date)
    ).values(
        'TRANSACTION_DATE',
        'TYPE',
        'TICKER',
        'IDENTIFIER',
        'QUANTITY',
        'AVG_BUY_PRICE',
        'AVG_SELL_PRICE',
        'COMMISSION',
        'FEES',
        'PROFIT_LOSS',
        'TRADE_START_TIME',
        'TRADE_END_TIME'
    )

    if not transactions:
        return JsonResponse({'message': 'No records found'}, status=404)

    df = pd.DataFrame(transactions)
    df['PROFIT_LOSS'] = pd.to_numeric(df['PROFIT_LOSS'], errors='coerce').fillna(0.0)
    total_profit_loss = df['PROFIT_LOSS'].sum()

    total_row = {
        'TRANSACTION_DATE': '',
        'TYPE': '',
        'TICKER': '',
        'IDENTIFIER': '',
        'QUANTITY': '',
        'AVG_BUY_PRICE': '',
        'AVG_SELL_PRICE': '',
        'COMMISSION': '',
        'FEES': 'Total_Profit_Loss',
        'PROFIT_LOSS': total_profit_loss,
        'TRADE_START_TIME': '',
        'TRADE_END_TIME': ''
    }
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    output = BytesIO()

    if file_type == 'xlsx':
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='TransactionData')
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        filename = 'transaction_data.xlsx'

    elif file_type == 'csv':
        df.to_csv(output, index=False)
        content_type = 'text/csv'
        filename = 'transaction_data.csv'

    elif file_type == 'pdf':
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        style = getSampleStyleSheet()

        elements.append(Paragraph("Transaction Report", style['Title']))
        elements.append(Spacer(1, 12))

        table_data = [df.columns.tolist()] + df.fillna("").astype(str).values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ]))
        elements.append(table)
        doc.build(elements)

        content_type = 'application/pdf'
        filename = 'transaction_data.pdf'

    else:
        return JsonResponse({'error': 'Invalid file_type. Use xlsx, csv, or pdf'}, status=400)

    output.seek(0)
    response = HttpResponse(output, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response



