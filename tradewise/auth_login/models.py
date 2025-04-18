from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import UserManager
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

class AdditionalInfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='username')
    timezone = models.CharField(max_length=150)
    currency = models.CharField(max_length=150)

    class Meta:
        db_table = 'additionalinfo'


class UserProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_photo = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = 'UserProfile'


AUTH_PROVIDERS = {'email':'email'}

class customer(AbstractBaseUser, PermissionsMixin):
    CUSTOMER_ID = models.IntegerField(primary_key=True, db_column='CUSTOMER_ID')
    EMAIL = models.EmailField(max_length=100, unique=True, db_column='USER_NAME')
    First_Name = models.CharField(max_length=50, db_column='FIRST_NAME')
    Last_Name = models.CharField(max_length=50, db_column='LAST_NAME')
    is_staff = models.CharField(max_length=1, default='N')
    is_superuser = models.CharField(max_length=1, default='N')
    is_verified = models.CharField(max_length=1, default='N')
    is_active = models.CharField(max_length=1, default='Y')
    CREATE_DATE = models.DateTimeField(auto_now_add=True, db_column='CREATE_DATE')
    CREATED_BY = models.CharField(max_length=100, db_column='CREATED_BY')
    last_login = models.DateTimeField(auto_now=True, db_column='LAST_LOGIN')
    Last_Updated_Date = models.DateTimeField(auto_now=True, db_column='LAST_UPDATED_DATE')
    Last_Updated_By = models.CharField(max_length=100, db_column='LAST_UPDATED_BY')
    auth_provider = models.CharField(max_length=100, default=AUTH_PROVIDERS.get("email"), db_column="AUTH_PROVIDER")

    USERNAME_FIELD = 'EMAIL'
    REQUIRED_FIELDS = ['First_Name', 'Last_Name']

    objects = UserManager()

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='customer_set',
        related_query_name='customer',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        related_name='customer_set',
        related_query_name='customer',
    )

    def save(self, *args, **kwargs):
        if not self.CUSTOMER_ID:
            last_customer = customer.objects.order_by('-CUSTOMER_ID').first()
            if not last_customer:
                self.CUSTOMER_ID = 100
            else:
                self.CUSTOMER_ID = last_customer.CUSTOMER_ID + 1
        super().save(*args, **kwargs)

    @property
    def get_full_name(self):
        return f"{self.First_Name} {self.Last_Name}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def __str__(self):
        return self.EMAIL

    class Meta:
        db_table = 'CUSTOMER'
