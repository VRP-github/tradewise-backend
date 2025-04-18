from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Tradewise!!")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('upload_file/', include('upload_file.urls')),  
    path('portfolio_organizer/', include('portfolio_organizer.urls')),
    path('analytics_report/', include('analytics_reports.urls')),
    path('comm_fees/', include('commission_fees.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('trade_log/', include('trade_log.urls')),
    path('auth_login/', include('auth_login.urls')),
    path('general_setting/', include('general_setting.urls')),
]
