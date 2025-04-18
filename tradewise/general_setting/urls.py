from . import views
from django.urls import path

urlpatterns = [
    path('profiles/create/', views.create_customer_profile, name='create_customer_profile'),
    path('profiles/edit/<str:customer_id>/', views.edit_customer_profile_by_customer_id, name='edit_customer_profile_by_customer_id'),
    path('profiles/get/<str:customer_id>/', views.get_customer_profiles_by_customer_id, name='get_customer_profiles_by_customer_id'),
    path('tradesettings/create/', views.create_trade_setting, name='create_trade_setting'),
    path('tradesettings/edit/', views.edit_trade_setting, name='edit_trade_setting_by_customer_id'),
    path('tradesettings/get/', views.get_trade_setting_by_customer_and_account, name='get_trade_setting_by_customer_and_account'),

]
