from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload_file/', include('upload_file.urls')),  
    path('portfolio_organizer/', include('portfolio_organizer.urls')),
    path('analytics_report/', include('analytics_reports.urls')),
    path('comm_fees/', include('commission_fees.urls'))
]
