from django.contrib import admin
from django.urls import path, include
from trade_log.views import home

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('upload_file/', include('upload_file.urls')),  
    path('portfolio_organizer/', include('portfolio_organizer.urls')),
    path('analytics_report/', include('analytics_reports.urls')),
    path('comm_fees/', include('commission_fees.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('trade_log/', include('trade_log.urls')),
]
