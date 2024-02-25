from django.contrib import admin
from user.models import User, Notification, Task

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'username', 'last_login')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task_name', 'task_status', 'created_at', 'end_date')
    list_filter = ('task_status',)
    list_editable = ('task_status',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'read', 'created_at')
