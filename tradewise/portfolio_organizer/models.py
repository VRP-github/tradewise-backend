from django.db import models

# Create your models here.
from django.db import models

class PortfolioOrganizer(models.Model):
    ACCOUNT_ID = models.CharField(max_length=10, primary_key=True)
    CUSTOMER_ID = models.CharField(max_length=255)
    ACCOUNT_NAME = models.CharField(max_length=100, unique=True)
    STOCK_TYPE = models.CharField(max_length=100)
    INITIAL_DEPOSIT = models.CharField(max_length=15, null=True, blank=True)
    IS_ACTIVE = models.CharField(max_length=1)
    CREATE_DATE = models.DateField()
    CREATED_BY = models.CharField(max_length=100)
    LAST_UPDATED_DATE = models.DateField()
    LAST_UPDATED_BY = models.CharField(max_length=100)
    PROFIT_CALCULATION_METHOD = models.CharField(max_length=100)
    BALANCE_DATE = models.DateTimeField()
    BALANCE_TIME = models.TimeField()
    BALANCE_DESCRIPTION = models.CharField(max_length=100)

    class Meta:
        db_table = 'PORTFOLIO_ORGANIZER'

    def save(self, *args, **kwargs):
        if not self.ACCOUNT_ID:
            last_account = PortfolioOrganizer.objects.order_by('ACCOUNT_ID').last()
            if not last_account:
                self.ACCOUNT_ID = "A100"
            else:
                try:
                    last_id = int(last_account.ACCOUNT_ID[1:])
                    self.ACCOUNT_ID = 'A' + str(last_id + 1)
                except ValueError:
                    self.ACCOUNT_ID = "A100"  # fallback if parsing fails
        super().save(*args, **kwargs)
