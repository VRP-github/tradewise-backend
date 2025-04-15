import pandas as pd
from django.http import JsonResponse
from django.utils.timezone import make_aware, is_naive, is_aware
from .parsing.parsing_csv import parsing_csv_trade_history, transaction_summary
from .parsing.parsing_xlsx import parsing_xlsx
from .parsing.parsing_html import parsing_html
from .validation.file_validation import validate_file
from .models import TransactionDetail, TransactionSummary, TransactionMapping
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import pytz
import traceback


@csrf_exempt
def upload_file(request, customer_id, account_id):
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file received'}, status=400)

        uploaded_file = request.FILES['file']
        filename = uploaded_file.name.lower()

        is_valid, validation_message = validate_file(uploaded_file)
        if not is_valid:
            return JsonResponse({'error': validation_message}, status=400)

        inserted_transaction_details = 0
        inserted_transaction_summaries = 0
        inserted_transaction_mappings = 0
        timezone = pytz.UTC

        parsed_data_trade_history = pd.DataFrame()
        parsed_data_summary = {}

        if filename.endswith('.csv'):
            trade_history_lines = []
            within_trade_history = False
            start_keyword_AT_History = "Account Trade History"
            end_keywords_AT_History = ["Cash Balance", "Portfolio Holdings", "Profits and Losses"]

            for line in uploaded_file:
                decoded_line = line.decode('utf-8').strip()
                if start_keyword_AT_History in decoded_line:
                    within_trade_history = True
                elif any(end_keyword in decoded_line for end_keyword in end_keywords_AT_History):
                    within_trade_history = False
                if within_trade_history:
                    trade_history_lines.append(decoded_line)

            if trade_history_lines:
                data_lines = [line.split(',') for line in trade_history_lines if line.strip() != '']
                num_columns = len(data_lines[0])
                data_lines = [line if len(line) == num_columns else line + [''] * (num_columns - len(line)) for line in data_lines]
                csv_df = pd.DataFrame(data_lines[1:], columns=data_lines[1]).dropna(axis=1, how='all')
                csv_df.columns = [col.strip() for col in csv_df.columns]
            else:
                csv_df = pd.DataFrame()

            if csv_df.empty:
                return JsonResponse({'error': 'The CSV file is empty.'}, status=400)

            parsed_data_trade_history = parsing_csv_trade_history(csv_df)
            parsed_data_summary = transaction_summary(parsed_data_trade_history)

        elif filename.endswith('.xlsx'):
            xlsx_df = pd.read_excel(uploaded_file)
            if xlsx_df.empty:
                return JsonResponse({'error': 'The XLSX file is empty.'}, status=400)

            parsed_data_trade_history = parsing_xlsx(xlsx_df)
            parsed_data_summary = transaction_summary(parsed_data_trade_history)

        elif filename.endswith('.html') or filename.endswith('.htm'):
            html_df = parsing_html(uploaded_file)
            if html_df.empty:
                return JsonResponse({'error': 'The HTML file is empty or invalid.'}, status=400)

            parsed_data_trade_history = html_df
            parsed_data_summary = transaction_summary(parsed_data_trade_history)

        else:
            return JsonResponse({'error': 'Invalid file type. Please upload a CSV, XLSX, HTML, or HTM file.'}, status=400)

        if parsed_data_trade_history.empty:
            return JsonResponse({"error": "Processed Dataframe is empty or invalid."}, status=400)

        # Insert TransactionDetail
        existing_rows = set(
            (identifier, make_aware(date) if is_naive(date) else date.astimezone(pytz.UTC), price, customer_id, account_id, txn_type)
            for identifier, date, price, customer_id, account_id, txn_type in TransactionDetail.objects.filter(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id
            ).values_list(
                'IDENTIFIER', 'TRANSACTION_DATE', 'PRICE', 'CUSTOMER_ID', 'ACCOUNT_ID', 'TYPE'
            )
        )

        for _, row in parsed_data_trade_history.iterrows():
            transaction_date = row['Exec Time']
            transaction_date = make_aware(transaction_date, timezone) if is_naive(transaction_date) else transaction_date.astimezone(timezone)

            key = (row['Transaction_Detail_ID'], transaction_date, row['Price'], customer_id, account_id, row['Type'])
            if key not in existing_rows:
                TransactionDetail.objects.create(
                    CUSTOMER_ID=customer_id,
                    ACCOUNT_ID=account_id,
                    TRANSACTION_DATE=transaction_date,
                    TYPE=row['Type'],
                    TICKER=row['Symbol'],
                    IDENTIFIER=row['Transaction_Detail_ID'],
                    QUANTITY=row['Qty'],
                    ORDER_TYPE=row['Order Type'],
                    PRICE=row['Price'],
                    IS_ACTIVE='Y',
                    CREATE_DATE=datetime.now(timezone).date(),
                    CREATED_BY='system',
                    FILENAME=filename,
                )
                inserted_transaction_details += 1

        # Insert TransactionSummary
        for summary in parsed_data_summary['data']:
            if summary['Is Processed'].upper() not in ('Y', 'N'):
                continue
            TransactionSummary.objects.create(
                CUSTOMER_ID=customer_id,
                ACCOUNT_ID=account_id,
                TRANSACTION_DATE=summary['Trade Start time'],
                TYPE=summary['Type'],
                TICKER=summary['TICKER'],
                IDENTIFIER=summary['IDENTIFIER'],
                QUANTITY=summary['QUANTITY'],
                AVG_BUY_PRICE=summary['Avg_Buy_Price'],
                AVG_SELL_PRICE=summary['Avg_Sell_Price'],
                PROFIT_LOSS=summary['Profit/Loss'],
                TRADE_START_TIME=summary['Trade Start time'],
                TRADE_END_TIME=summary['Trade End time'],
                IS_ACTIVE='Y',
                CREATE_DATE=datetime.now(timezone).date(),
                CREATED_BY='system',
                IS_PROCESSED=summary['Is Processed'].upper(),
            )
            inserted_transaction_summaries += 1

        # Insert TransactionMapping
        summaries = TransactionSummary.objects.filter(IS_PROCESSED='Y').values_list(
            'TRANSACTION_SUMMARY_ID', 'TRADE_START_TIME', 'TRADE_END_TIME', 'IDENTIFIER'
        )
        details = TransactionDetail.objects.values_list(
            'TRANSACTION_DETAIL_ID', 'IDENTIFIER', 'TRANSACTION_DATE'
        )

        for ts_id, start, end, ident in summaries:
            if not start or not end:
                continue

            if isinstance(start, datetime):
                start_dt = start
            else:
                start_dt = datetime.combine(start, datetime.min.time())

            if isinstance(end, datetime):
                end_dt = end
            else:
                end_dt = datetime.combine(end, datetime.max.time())

            if not is_aware(start_dt):
                start_dt = make_aware(start_dt, timezone)
            if not is_aware(end_dt):
                end_dt = make_aware(end_dt, timezone)

            for td_id, det_ident, det_time in details:
                if not det_time:
                    continue

                if not isinstance(det_time, datetime):
                    det_time = datetime.combine(det_time, datetime.min.time())

                if not is_aware(det_time):
                    det_time = make_aware(det_time, timezone)
                else:
                    det_time = det_time.astimezone(timezone)

                if start_dt <= det_time <= end_dt and ident == det_ident:
                    try:
                        TransactionMapping.objects.create(
                            CUSTOMER_ID=customer_id,
                            ACCOUNT_ID=account_id,
                            TRANSACTION_SUMMARY_ID=ts_id,
                            TRANSACTION_DETAIL_ID=td_id,
                            IS_ACTIVE='Y',
                            CREATE_DATE=datetime.now(timezone).date(),
                            CREATED_BY='system',
                        )
                        inserted_transaction_mappings += 1
                    except Exception as e:
                        print(f"Mapping insert error: {e}")

        return JsonResponse({
            "message": f"Transaction details and summaries inserted successfully ({filename}).",
            "transaction_details_inserted": inserted_transaction_details,
            "transaction_summaries_inserted": inserted_transaction_summaries,
            "transaction_mappings_inserted": inserted_transaction_mappings
        })

    except Exception as e:
        full_traceback = traceback.format_exc()
        return JsonResponse({'error': f'An error occurred while processing the request by viraj: {str(e)}'}, status=500)