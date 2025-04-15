from django.db import models
from django.utils import timezone 

class TradeLogs(models.Model):
    TRADE_LOG_ID = models.CharField(max_length=10, primary_key=True)
    CUSTOMER_ID = models.CharField(max_length=10)
    ACCOUNT_ID = models.CharField(max_length=10)
    FILE_NAME = models.CharField(max_length=255)
    UPLOAD_TIME = models.DateTimeField(default=timezone.now)
    TOTAL_ENTRIES = models.IntegerField()
    DUPLICATE_ENTRIES = models.IntegerField()
    CREATE_DATE = models.DateField(default=timezone.now)
    CREATED_BY = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'TRADE_LOGS'

    def __str__(self):
        return self.TRADE_LOG_ID

    def save(self, *args, **kwargs):
        if not self.TRADE_LOG_ID:
            last_log = TradeLogs.objects.order_by('TRADE_LOG_ID').last()
            if not last_log:
                self.TRADE_LOG_ID = "TL100"
            else:
                try:
                    last_id = int(last_log.TRADE_LOG_ID[2:])
                    self.TRADE_LOG_ID = 'TL' + str(last_id + 1)
                except ValueError:
                    self.TRADE_LOG_ID = "TL100"
        super().save(*args, **kwargs)
