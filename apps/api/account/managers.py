from django.contrib.auth.models import BaseUserManager
from django_softdelete.models import SoftDeleteManager


class UserManager(BaseUserManager, SoftDeleteManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("The Email field is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_admin", True)

        if extra_fields.get("is_admin") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, password, **extra_fields)
