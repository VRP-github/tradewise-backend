
from django.urls import path
from . import views

urlpatterns = [
    path('fetch-account-names/', views.fetch_account_names, name='fetch_account_names'),
    path('fetch-account-symbols/', views.fetch_account_symbols, name='fetch_account_symbols'),
    path('fetch_download_data/', views.fetch_download_data, name="fetch_download_data"),
]
