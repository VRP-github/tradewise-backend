from django.db import models
from auth_login.models import customer

class CustomerProfile(models.Model):
    profile_id = models.AutoField(primary_key=True) 
    customer_id = models.ForeignKey(customer, on_delete=models.CASCADE, db_column="customer_id")
    timezone = models.CharField(max_length=50)
    currency = models.CharField(max_length=3)
    is_active = models.CharField(max_length=1, default='Y')

    class Meta:
        db_table = 'auth_login_customer_profile'

    def save(self, *args, **kwargs):
        if not self.profile_id:
            last_profile = CustomerProfile.objects.order_by('profile_id').last()
            if not last_profile:
                self.profile_id = 1
            else:
                self.profile_id = last_profile.profile_id + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Profile ID: {self.profile_id}, Customer ID: {self.customer_id}'

from django.db import models
from auth_login.models import customer

class TradeSetting(models.Model):
    trade_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(customer, on_delete=models.CASCADE, db_column="customer_id")
    account_id = models.CharField(max_length=100, unique=True)  
    type = models.CharField(max_length=50)
    from_field = models.CharField(max_length=50, db_column="from_value")
    to_field = models.CharField(max_length=50, db_column="to_value")

    class Meta:
        db_table = 'auth_login_trade_setting'

    def __str__(self):
        return f"TradeSetting #{self.trade_id} | Customer: {self.customer_id} | Account: {self.account_id}"
