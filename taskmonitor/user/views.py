from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from user.models import User, Task, Notification, ScreenShot
from django.contrib.auth import authenticate, login, logout
from reportlab.pdfgen import canvas
from datetime import datetime
from django.conf import settings

def MakePayment(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not request.user.is_staff:
        return redirect('home')
    
    user = User.objects.get(user_id=pk)
    user.work_minutes =0
    user.save()
    return JsonResponse({"success":True})

class Payment(View):
    template_name = "payment.html"

    def get(self, request):
        return render(request=request, template_name=self.template_name, context={"hour_rate":settings.HOUR_RATE})

def AddWorkMinute(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        if not request.user.paused:
            request.session["time"] += 10
            if request.session["time"] == 60:
                request.user.work_minutes += 1
                request.user.save()
                request.session["time"] = 0
    
    except Exception as e:
        pass

    return JsonResponse({"success": True})

def TogglePause(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        request.user.paused = not request.user.paused
        request.user.save()
        pass
    
    except Exception as e:
        pass

    return redirect('home')

class UserScreenshot(View):
    template_name = 'admin/screenshot.html'

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_staff:
            return redirect('home')
        
        try:
            screenshot = ScreenShot.objects.get(screenshot_id=pk)
            return render(request=request, template_name=self.template_name, context={"screenshot":screenshot})
        
        except Exception as e:
            return JsonResponse({"success": str(e)})

class GenerateUserReportPdf(View):
    def get(self, request, user_id):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            user = User.objects.get(user_id=user_id)
            tasks = Task.objects.filter(user=user)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="user_report.pdf"'
            p = canvas.Canvas(response)
            p.drawString(100, 100, f"User ID: {user.user_id}")
            p.drawString(100, 80, f"Username: {user.username}")
            p.drawString(100, 60, f"Staff ID: {user.staff_id}")
            p.drawString(100, 40, f"Total Tasks: {len(tasks)}")
            p.drawString(100, 20, f"Active Tasks: {len(Task.objects.filter(user=user, task_status='active'))}")
            for i in range(len(tasks)):
                p.drawString(100, 20*(i+1), f"{i+1}. {tasks[i].task_name}  - {tasks[i].task_status}")
                
            p.showPage()
            p.save()
            return response
        
        except Exception as e:
            return JsonResponse({"success": str(e)})



class UpdateTaskStatus(View):
    def get(self, request, task_id, status):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            task = Task.objects.get(task_id=task_id)
            task.task_status = status
            task.finish_date = datetime.now()
            task.save()
            return redirect('home')
        
        except Exception as e:
            return JsonResponse({"success": str(e)})

class Notifications(View):
    template_name = "notifications.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        context = {'notifications' : Notification.objects.filter(user=request.user)}
        return render(request=request, template_name=self.template_name, context=context)

class AddTask(View):
    template_name = "admin/add_task.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_staff:
            return redirect('home')
        
        context = {'users' : User.objects.filter(is_staff=False)}

        return render(request=request, template_name=self.template_name, context=context)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_staff:
            return redirect('home')
        
        context = {
            "userdata": {
                "user_id": request.POST['user'],
                "task_name": request.POST['task_name'],
                "task_deadline": request.POST['end_date'],
            },
            "success": True,
            "error": {}
        }

        for field in context["userdata"]:
            if not context["userdata"][field]:
                context["success"] = False
                context["error"][field] = "This field is required."

        if not context["success"]:
            return render(request=request, template_name=self.template_name, context=context)
        
        try:
            user = User.objects.get(user_id=context["userdata"]["user_id"])
            task = Task(
                user = user,
                task_name = context["userdata"]["task_name"],
                end_date = context["userdata"]["task_deadline"]
            )
            task.save()
            notification = Notification(
                user = user,
                message = f"You have been assigned a new task: {task.task_name}" 
            )
            notification.save()
            return redirect(f'/user-details/{context["userdata"]["user_id"]}/')
        
        except User.DoesNotExist:
            context["error"]["user_id"] = "Invalid user ID"
            return render(request=request, template_name=self.template_name, context=context)

class UserTaskDetails(View):
    template_name = "admin/user_details.html"

    def get(self, request, user_id):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_staff:
            return redirect('home')
        
        try:
            user = User.objects.get(user_id=user_id)
            screenshots = ScreenShot.objects.filter(user=user).order_by('-created_at')
            context = {'tasks' : Task.objects.filter(user=user), 'vuser': user, 'screenshots': screenshots,"hour_rate":settings.HOUR_RATE}
            return render(request=request, template_name=self.template_name, context=context)            
        
        except Task.DoesNotExist:
            return redirect('home')


class TaskHistory(View):
    template_name = "task_history.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        context = {'tasks' : Task.objects.filter(user=request.user)}
        return render(request=request, template_name=self.template_name, context=context)

@method_decorator(csrf_exempt, name='dispatch')
class SaveScreenshot(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.paused:
            return JsonResponse({"success": True})
        
        print(request.user.is_staff)
        
        try:
            screenshot = ScreenShot(
                user = request.user,
                image = request.FILES['screenshot']
            )
            screenshot.save()
            return JsonResponse({"success": True})
        
        except Exception as e:
            return JsonResponse({"success": str(e)})

class Profile(View):
    template_name = 'auth/profile.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        return render(request=request, template_name=self.template_name)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        context = {
            "userdata": {
                "password": request.POST['password'],
                "password1": request.POST['password1'],
                "password2": request.POST['password2']
            },
            "success": True,
            "error": {}
        }

        if not request.user.check_password(context["userdata"]["password"]):
            context["error"]["password"] = "Invalid password"
            return render(request=request, template_name=self.template_name, context=context)

        if len(context["userdata"]["password1"]) < 8:
            context["error"]["password1"] = "Password must be at least 8 characters long."
            return render(request=request, template_name=self.template_name, context=context)

        if context["userdata"]["password1"] != context["userdata"]["password2"]:
            context["error"]["password2"] = "Your passwords do not match"
            return render(request=request, template_name=self.template_name, context=context)

        request.user.set_password(context["userdata"]["password1"])
        request.user.save()

        return redirect('logout')
    
class TaskDetails(View):
    template_name = "task_details.html"
    admin_template_name = "admin/task_details.html"

    def get(self, request, task_id):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            if request.user.is_staff:
                task = Task.objects.get(task_id=task_id)
                context = {'task' : task}
                return render(request=request, template_name=self.admin_template_name, context=context)  

            task = Task.objects.get(task_id=task_id, user=request.user)
            context = {'task' : task}
            return render(request=request, template_name=self.template_name, context=context)          
        
        except Task.DoesNotExist:
            return redirect('home')

class Home(View):
    template_name = "home.html"
    admin_template_name = "admin/home.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.is_staff:
            context = {'users' : User.objects.all()}
            return render(request=request, template_name=self.admin_template_name, context=context)
        
        context = {'tasks' : Task.objects.filter(user=request.user, task_status='active')}
        return render(request=request, template_name=self.template_name, context=context)
    
def Logout(request):
    logout(request=request)
    return redirect("login")


class Login(View):
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        return render(request=request, template_name=self.template_name)
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        context = {
            "userdata": {
                "staff_id": request.POST['staff_id'].upper(),
                "password": request.POST['password']
            },
            "success": True,
            "error": {}
        }

        for field in context["userdata"]:
            if not context["userdata"][field]:
                context["success"] = False
                context["error"][field] = "This field is required."

        if not context["success"]:
            return render(request=request, template_name=self.template_name, context=context)

        try:
            User.objects.get(staff_id=context["userdata"]["staff_id"])

            user = authenticate(
                    request=request, 
                    staff_id=context["userdata"]["staff_id"].upper(), 
                    password=context["userdata"]["password"]
                )
            
            if not user:
                context["error"]["all"] = "Invalid login credentials"
                return render(request=request, template_name=self.template_name, context=context)

            login(request=request, user = user)
            request.session["time"] = 0
            return redirect('home')
            
        except User.DoesNotExist:
            context["error"]["all"] = "Invalid login credentials"
            return render(request=request, template_name=self.template_name, context=context)
        

class Register(View):
    template_name = 'auth/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        return render(request=request, template_name=self.template_name)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        context = {
            "userdata": {
                "staff_id": request.POST['staff_id'].upper(),
                "username": request.POST['username'].upper(),
                "password1": request.POST['password1'],
                "password2": request.POST['password2']
            },
            "success": True,
            "error": {}
        }

        for field in context["userdata"]:
            if not context["userdata"][field]:
                context["success"] = False
                context["error"][field] = "This field is required."

        if not context["success"]:
            return render(request=request, template_name=self.template_name, context=context)

        if len(context["userdata"]["password1"]) < 8:
            context["error"]["password1"] = "Password must be at least 8 characters long."
            return render(request=request, template_name=self.template_name, context=context)

        if context["userdata"]["password1"] != context["userdata"]["password2"]:
            context["error"]["password2"] = "Passwords do not match."
            return render(request=request, template_name=self.template_name, context=context)

        user = User(
            username=context["userdata"]["username"].upper(),
            staff_id=context["userdata"]["staff_id"]
        )

        user.set_password(context["userdata"]["password1"])
        user.save()
        return redirect('login')

