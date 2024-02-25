from django.urls import path
from user.views import Register, Login, Logout, Home, Profile, SaveScreenshot, UserTaskDetails, TaskHistory, TaskDetails, Notifications, AddTask, UpdateTaskStatus, UserScreenshot, TogglePause, AddWorkMinute, Payment

urlpatterns = [
    path(route='payment/', view=Payment.as_view(), name='payment'),
    path(route='add-minute/', view=AddWorkMinute, name='add-minute'),
    path(route='pause/', view=TogglePause, name='pause'),
    path(route='save-screenshot/', view=SaveScreenshot.as_view(), name='save-screenshot'),
    path(route='<pk>/screenshot/', view=UserScreenshot.as_view(), name='screenshot'),
    path(route="profile/", view=Profile.as_view(), name="profile"),
    path(route="login/", view=Login.as_view(), name='login'),
    path(route='register/', view=Register.as_view(), name='register'),
    path(route="logout/", view=Logout, name='logout'),
    path(route="task-history/", view=TaskHistory.as_view(), name='task-history'),
    path(route="task-details/<str:task_id>/", view=TaskDetails.as_view(), name='task-details'),
    path(route="user-details/<str:user_id>/", view=UserTaskDetails.as_view(), name='user-details'),
    path(route="notifications/", view=Notifications.as_view(), name='notifications'),
    path(route="update-status/<str:task_id>/<str:status>/", view=UpdateTaskStatus.as_view(), name='update-status'),
    path(route="add-task/", view=AddTask.as_view(), name='add-task'),
    path(route="", view=Home.as_view(), name='home')
]