from django.db import models, connection
from django.utils import timezone


def insert_transactions(parsed_data):
    try:
        with connection.cursor() as cursor:
            for entry in parsed_data:
                date, time, type_, ref_number, trade_action, quantity, symbol, net_quantity, duration, predicted_date, predicted_rate, put_call, rate, exchange_center, misc_fees, commissions_fees, amount, balance = entry

                cursor.execute(
                    """
                    INSERT INTO transactions (
                        "Date", "Time", "Type", "RefNumber", "TradeAction", "Quantity", "Symbol", "NetQuantity", "Duration",
                        "PredictedDate", "PredictedRate", "PutCall", "Rate", "ExchangeCenter", "MiscFees", "CommissionsFees", "Amount", "Balance"
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (date, time, type_, ref_number, trade_action, quantity, symbol, net_quantity, duration,
                     predicted_date, predicted_rate, put_call, rate, exchange_center, misc_fees, commissions_fees,
                     amount, balance)
                )
            connection.commit()
            return {'message': 'File received and data inserted successfully', 'data': parsed_data}, 200

    except Exception as e:
        connection.rollback()
        return {'error': f'Error inserting data into database: {str(e)}'}, 500


class TransactionDetail(models.Model):
    TRANSACTION_DETAIL_ID = models.CharField(max_length=10, primary_key=True)
    CUSTOMER_ID = models.CharField(max_length=10)
    ACCOUNT_ID = models.CharField(max_length=10)
    TRANSACTION_DATE = models.DateTimeField()
    TYPE = models.CharField(max_length=10)
    TICKER = models.CharField(max_length=10)
    IDENTIFIER = models.CharField(max_length=50)
    QUANTITY = models.FloatField()
    ORDER_TYPE = models.CharField(max_length=10)
    PRICE = models.CharField(max_length=10)
    IS_ACTIVE = models.CharField(max_length=1)
    CREATE_DATE = models.DateField()
    CREATED_BY = models.CharField(max_length=100)
    FILENAME = models.CharField(max_length=100, default='unknown_file.csv')

    class Meta:
        db_table = 'TRANSACTION_DETAIL'

    def __str__(self):
        return self.TRANSACTION_DETAIL_ID

    def save(self, *args, **kwargs):
        if not self.TRANSACTION_DETAIL_ID:
            last_id_obj = TransactionDetail.objects \
                .extra(select={'numeric_id': "CAST(SUBSTRING(\"TRANSACTION_DETAIL_ID\" FROM 3) AS INTEGER)"}) \
                .order_by('-numeric_id') \
                .first()
            self.TRANSACTION_DETAIL_ID = f'TD{(int(last_id_obj.TRANSACTION_DETAIL_ID[2:]) + 1) if last_id_obj else 100}'
        super().save(*args, **kwargs)


class Commission(models.Model):
    COMMISSION_ID = models.CharField(max_length=10, primary_key=True)
    CUSTOMER_ID = models.CharField(max_length=10)
    ACCOUNT_ID = models.CharField(max_length=10)
    TRANSACTION_DETAIL_ID = models.CharField(max_length=10)
    FEE = models.CharField(max_length=10)
    COMMISSION = models.CharField(max_length=10)
    IS_ACTIVE = models.CharField(max_length=1)
    CREATE_DATE = models.DateField(default=timezone.now)
    CREATED_BY = models.CharField(max_length=100)

    class Meta:
        db_table = 'COMMISSION'

    def __str__(self):
        return self.COMMISSION_ID

    def save(self, *args, **kwargs):
        if not self.COMMISSION_ID:
            last_id_obj = Commission.objects \
                .extra(select={'numeric_id': "CAST(SUBSTRING(\"COMMISSION_ID\" FROM 3) AS INTEGER)"}) \
                .order_by('-numeric_id') \
                .first()
            self.COMMISSION_ID = f'CM{(int(last_id_obj.COMMISSION_ID[2:]) + 1) if last_id_obj else 100}'
        super().save(*args, **kwargs)


class TransactionSummary(models.Model):
    TRANSACTION_SUMMARY_ID = models.CharField(max_length=10, primary_key=True)
    CUSTOMER_ID = models.CharField(max_length=10)
    ACCOUNT_ID = models.CharField(max_length=10)
    TRANSACTION_DATE = models.DateField()
    TYPE = models.CharField(max_length=10)
    TICKER = models.CharField(max_length=10)
    IDENTIFIER = models.CharField(max_length=50)
    QUANTITY = models.FloatField()
    AVG_BUY_PRICE = models.CharField(max_length=50)
    AVG_SELL_PRICE = models.CharField(max_length=50, null=True, blank=True)
    COMMISSION = models.CharField(max_length=15, null=True, blank=True)
    FEES = models.CharField(max_length=15, null=True, blank=True)
    PROFIT_LOSS = models.CharField(max_length=50)
    TRADE_START_TIME = models.DateField()
    TRADE_END_TIME = models.DateField(null=True, blank=True)
    TRADE_DURATION = models.CharField(max_length=10, null=True, blank=True)
    IS_ACTIVE = models.CharField(max_length=1)
    CREATE_DATE = models.DateField()
    CREATED_BY = models.CharField(max_length=100)
    IS_PROCESSED = models.CharField(max_length=10)

    class Meta:
        db_table = 'TRANSACTION_SUMMARY'

    def save(self, *args, **kwargs):
        if not self.TRANSACTION_SUMMARY_ID:
            last_id_obj = TransactionSummary.objects \
                .extra(select={'numeric_id': "CAST(SUBSTRING(\"TRANSACTION_SUMMARY_ID\" FROM 3) AS INTEGER)"}) \
                .order_by('-numeric_id') \
                .first()
            self.TRANSACTION_SUMMARY_ID = f'TS{(int(last_id_obj.TRANSACTION_SUMMARY_ID[2:]) + 1) if last_id_obj else 100}'
        super().save(*args, **kwargs)


class TransactionMapping(models.Model):
    TRANSACTION_MAPPING_ID = models.CharField(max_length=15, primary_key=True)
    CUSTOMER_ID = models.CharField(max_length=10)
    ACCOUNT_ID = models.CharField(max_length=10)
    TRANSACTION_SUMMARY_ID = models.CharField(max_length=10)
    TRANSACTION_DETAIL_ID = models.CharField(max_length=10)
    IS_ACTIVE = models.CharField(max_length=1)
    CREATE_DATE = models.DateField()
    CREATED_BY = models.CharField(max_length=100)

    class Meta:
        db_table = 'TRANSACTION_MAPPING'

    def save(self, *args, **kwargs):
        if not self.TRANSACTION_MAPPING_ID:
            last_id_obj = TransactionMapping.objects \
                .extra(select={'numeric_id': "CAST(SUBSTRING(\"TRANSACTION_MAPPING_ID\" FROM 3) AS INTEGER)"}) \
                .order_by('-numeric_id') \
                .first()
            self.TRANSACTION_MAPPING_ID = f'TM{(int(last_id_obj.TRANSACTION_MAPPING_ID[2:]) + 1) if last_id_obj else 100}'
        super().save(*args, **kwargs)
