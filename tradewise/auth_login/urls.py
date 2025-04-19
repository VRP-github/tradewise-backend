from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('profile/', views.TestAuthenticationView.as_view(), name="granted"),
    path('logout/', views.LogoutUserView.as_view(), name="logout"),
    path('customer_profile_detail/<str:customer_id>/', views.customer_info, name="customer_profile_detail"),
    path('edit_customer/<str:customer_id>/', views.edit_customer_info, name='edit_customer_info'),
    path('change_password/<str:customer_id>/', views.change_customer_password, name='change_customer_password'),
    path('recover_account/', views.recover_account, name='recover_account'),
]
