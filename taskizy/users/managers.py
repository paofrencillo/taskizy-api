from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Customize User Manager for creating and validating new users.
    """

    def email_validator(self, email):
        """
        Validate email and check for errors.
        """
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Provide a valid email."))

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        """
        Validate created user and check for errors.
        """
        if not first_name:
            raise ValueError(_("You must provide a first name."))

        if not last_name:
            raise ValueError(_("You must provide a last name."))

        if email:
            normalized_email = self.normalize_email(email)
            self.email_validator(normalized_email)
        else:
            raise ValueError(_("Email address is required."))

        if not password:
            raise ValueError(_("Password is required"))

        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )

        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user.save()

        return user

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        """
        Validate created superuser and check for errors.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser value of 'is_staff' should be True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser value of 'is_superuser' should be True."))

        if extra_fields.get("is_active") is not True:
            raise ValueError(_("Superuser value of 'is_active' should be True."))

        if not first_name:
            raise ValueError(_("You must provide a first name."))

        if not last_name:
            raise ValueError(_("You must provide a last name."))

        if email:
            normalized_email = self.normalize_email(email)
            self.email_validator(normalized_email)
        else:
            raise ValueError(_("Email address is required."))

        if not password:
            raise ValueError(_("Password is required"))

        user = self.create_user(first_name, last_name, email, password, **extra_fields)

        user.save()

        return user
