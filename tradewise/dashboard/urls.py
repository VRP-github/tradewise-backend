from django.urls import path
from . import views

urlpatterns = [
    path('profit_loss/', views.total_profit_loss, name='total_profit_loss'),
    path('win_percentage/', views.calculate_profit_percentage, name='calculate_profit_percentage'),
    path('profit_factor/', views.calculate_profit_factor, name='calculate_profit_factor'),
    path('avg_win_loss_ratio/', views.calculate_avg_win_loss_ratio, name='calculate_avg_win_loss_ratio'),
    path('closed_transaction/', views.get_zero_quantity_transactions, name='zero_quantity_transactions'),
    path('transaction_graph/', views.get_transaction_details, name='get_transaction_details'),
]
