from django.db import models
from accounts.models import Account
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='profile')
    auth_token  = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return self.user.username