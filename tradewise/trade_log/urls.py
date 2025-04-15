
from django.urls import path
from . import views

urlpatterns = [
    path('log_uploaded_filenames/', views.log_uploaded_filenames, name='log_uploaded_filenames'),
    path('get_trade_logs/', views.get_trade_logs_by_customer_account, name='get_trade_logs'),
    path('get_trade_logs_by_date/', views.get_trade_logs_by_date_range, name='get_trade_logs_by_date'),
]
