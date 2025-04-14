from django.urls import path
from .views import upload_file

urlpatterns = [
    path('file/<str:customer_id>/<str:account_id>/', upload_file, name='upload_file'),
    # path('fetch_transaction_summary/', fetch_transaction_summary, name='fetch_transaction_summary'),
]
