from django.urls import path
from .views import fetch_account_names, update_transaction_commission_fees  

urlpatterns = [
    path('fetch-account-names/', fetch_account_names, name='fetch_account_names'),
    path('update-transactions/', update_transaction_commission_fees, name='update_transaction_commission_fees'),
]
