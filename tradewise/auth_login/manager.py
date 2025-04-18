from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def email_validator(self, EMAIL):
        try:
            validate_email(EMAIL)
        except ValidationError:
            raise ValueError(_("Please enter a valid email address"))

    def create_user(self, EMAIL, First_Name, Last_Name,password=None,**extra_fields):
        if not EMAIL:
            raise ValueError(_("An Email address is required"))
        EMAIL = self.normalize_email(EMAIL)
        self.email_validator(EMAIL)
        if not First_Name:
            raise ValueError(_("First Name is required"))
        if not Last_Name:
            raise ValueError(_("Last Name is required"))

        extra_fields.setdefault('is_staff', 'N')
        extra_fields.setdefault('is_superuser', 'N')
        extra_fields.setdefault('is_verified', 'N')
        extra_fields.setdefault('is_active', 'Y')
        extra_fields.setdefault('CREATED_BY', EMAIL)
        extra_fields.setdefault('Last_Updated_By', EMAIL)

        user = self.model(
            EMAIL=EMAIL,
            First_Name=First_Name,
            Last_Name=Last_Name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, EMAIL, First_Name, Last_Name,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', 'Y')
        extra_fields.setdefault('is_superuser', 'Y')
        extra_fields.setdefault('is_verified', 'Y')
        extra_fields.setdefault('is_active', 'Y')

        if extra_fields.get('is_staff') != 'Y':
            raise ValueError(_("Superuser must have is_staff='Y'"))
        if extra_fields.get('is_superuser') != 'Y':
            raise ValueError(_("Superuser must have is_superuser='Y'"))

        user = self.create_user(
            EMAIL, First_Name, Last_Name,password, **extra_fields
        )
        user.save(using=self._db)

        return user


