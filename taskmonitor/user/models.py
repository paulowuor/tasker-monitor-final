from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from uuid import uuid4
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, staff_id, username, password):
        user = self.model()
        user.username = username
        user.staff_id = staff_id
        user.set_password(password)
        user.save(using  = self.db)
        return user

    def create_superuser(self, staff_id, username, password):
        user = self.create_user(
            staff_id=staff_id,
            username=username,
            password=password
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using  = self.db)
        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(unique=True, default=uuid4)
    staff_id = models.CharField(max_length=10, unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    work_minutes = models.BigIntegerField(default=0)
    paused = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.staff_id

    USERNAME_FIELD = 'staff_id'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def all_tasks(self):
        try:
            return len(Task.objects.filter(user=self))
        
        except Exception as e:
            return 0

    def active_tasks(self):
        try:
            return len(Task.objects.filter(user=self, task_status="active"))
        
        except Exception as e:
            return 0
        
    def completed_tasks(self):
        try:
            return len(Task.objects.filter(user=self, task_status="completed"))
        
        except Exception as e:
            return 0
        
    def cancelled_tasks(self):
        try:
            return len(Task.objects.filter(user=self, task_status="cancelled"))
        
        except Exception as e:
            return 0
        
    def expired_tasks(self):
        try:
            return len(Task.objects.filter(user=self, task_status="expired"))
        
        except Exception as e:
            return 0
        
    def work_hours(self):
        hours, remainder = divmod(self.work_minutes, 60)
        formatted_time = "{:02d}:{:02d}".format(hours, remainder)

        return formatted_time
    
    def payment(self):
        time = self.work_minutes/60
        amount = time * settings.HOUR_RATE
        return round(amount, 2)


class Notification(models.Model):
    notification_id = models.UUIDField(unique=True, default=uuid4)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='send_on')

        
task_statuses = (
    ('active', 'active'),
    ('completed', 'completed'),
    ('cancelled', 'cancelled'),
    ('expired', 'expired')
)
class Task(models.Model):
    task_id = models.UUIDField(unique=True, default=uuid4)
    task_name = models.CharField(max_length=20)
    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True, blank=True)
    task_status = models.CharField(max_length=20, choices=task_statuses, default='active')
    finish_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='start_date')

    def __str__(self) -> str:
        return self.task_name
    
    def cancel(self):
        self.task_status = 'cancelled'
        self.save()
    
    def complete(self):
        self.task_status = 'completed'
        self.save()

    def duration(self):
        if self.finish_date:
            return self.finish_date - self.created_at
        
        else:
            return 'on going'


class ScreenShot(models.Model):
    screenshot_id = models.UUIDField(unique=True, default=uuid4)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='screenshot/') 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='taken_on')   