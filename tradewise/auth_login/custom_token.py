from django.db import models
from django.conf import settings
from rest_framework_simplejwt.models import AbstractToken, BlacklistedTokenMixin

class CustomOutstandingToken(AbstractToken):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='custom_outstanding_tokens',
        to_field='CUSTOMER_ID',  
        db_column='user_id'
    )

class CustomBlacklistedToken(BlacklistedTokenMixin):
    token = models.OneToOneField(
        CustomOutstandingToken,
        on_delete=models.CASCADE,
        related_name='blacklist_token'
    )
