from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self,email, password=None, **extra_fields):

        #check if not empty
        if not email or 'first_name' not in extra_fields or 'last_name' not in extra_fields:
            raise ValueError("Les champs nom, prénom, email sont obligatoire")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) #hash password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True) #if no value inserted for is_staff set as default to true
        extra_fields.setdefault('is_superuser', True)

        #check if is_staff is set to True before creating user
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Un superuser doit avoir is_staff=True")
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False) 
    is_staff = models.BooleanField(default=False)

    # use MemberManager instead of default manager 
    objects = UserManager()

    USERNAME_FIELD = 'email' #use email as principal instead of username

    # string return of a member object
    def __str__(self):
        return f'{self.email} - {self.last_name.upper()} {self.first_name} - is student :  {self.is_student} - is teacher : {self.is_teacher} - is staff : {self.is_staff}'