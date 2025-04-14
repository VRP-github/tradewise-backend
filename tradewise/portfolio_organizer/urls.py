from django.urls import path
from .views import insert_account, get_active_portfolio_accounts, update_portfolio_account, delete_portfolio_account

urlpatterns = [
    path('insert_account/<str:customer_id>/', insert_account, name='insert_account'),
    path('get_active_portfolio_accounts/<str:customer_id>/', get_active_portfolio_accounts, name='get_active_portfolio_accounts'),
    path('update_account/<str:account_id>/', update_portfolio_account, name='update_portfolio_account'),
    path('delete_account/<str:customer_id>/<str:account_id>/', delete_portfolio_account, name='delete_portfolio_account'),
]
