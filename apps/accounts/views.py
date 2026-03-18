from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, faculty_required, student_required

from django.urls import reverse_lazy

from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.views import LoginView, LogoutView


from academics.models import Subject
from accounts.models import CustomUser
from exams.models import Exam , Question ,StudentExam

from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


# def home(request):
#     # Smart Routing: If they are already logged in, send them to their dashboard!
#     if request.user.is_authenticated:
#         if getattr(request.user, 'role', None) == 'faculty':
#             return redirect('faculty_dashboard')
#         elif getattr(request.user, 'role', None) == 'student':
#             return redirect('student_dashboard')
#         elif request.user.is_superuser:
#             return redirect('/admin/')
            
#     # If they are not logged in, show them the beautiful landing page
#     return render(request, 'home.html')

def home(request):
    # Bypass: If you add ?view=home to the URL, it will stay on the home page
    if request.GET.get('view') == 'home':
        return render(request, 'home.html')

    # Smart Routing: If they are already logged in, send them to their dashboard!
    if request.user.is_authenticated:
        if getattr(request.user, 'role', None) == 'faculty':
            return redirect('faculty_dashboard')
        elif getattr(request.user, 'role', None) == 'student':
            return redirect('student_dashboard')
        elif request.user.is_superuser or getattr(request.user, 'role', None) == 'admin':
            return redirect('admin_dashboard') # FIXED: Now redirects to your Custom Dashboard!
            
    # If they are not logged in, show them the beautiful landing page
    return render(request, 'home.html')
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        # Redirect based on User Role
        user = self.request.user
        if user.role == 'admin':
            return reverse_lazy('admin_dashboard') # We will create this URL later
        elif user.role == 'faculty':
            return reverse_lazy('faculty_dashboard')
        elif user.role == 'student':
            return reverse_lazy('student_dashboard')
        return reverse_lazy('login')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)
    
@login_required
@admin_required
def admin_dashboard(request):
    # 1. Calculate Real Statistics
    total_students = CustomUser.objects.filter(role='student').count()
    total_faculty = CustomUser.objects.filter(role='faculty').count()
    
    # Active exams are exams that have not ended yet
    now = timezone.now()
    active_exams = Exam.objects.filter(end_time__gte=now).count()

    # 2. Fetch the 5 most recently registered users (excluding the superuser)
    recent_users = CustomUser.objects.exclude(is_superuser=True).order_by('-date_joined')[:5]

    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'active_exams': active_exams,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
@login_required
@faculty_required
def faculty_dashboard(request):
    return render(request, 'dashboard/faculty_dashboard.html')

@login_required
@student_required
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')


# todo |  Faculty dashboard and functions


@login_required
@faculty_required
def faculty_dashboard(request):
    # 1. Get subjects assigned to this specific faculty member
    my_subjects = Subject.objects.filter(faculty=request.user)
    
    # 2. Get exams created by this faculty
    my_exams = Exam.objects.filter(created_by=request.user).order_by('-start_time')
    
    # 3. Count total questions in the bank for their subjects
    my_subject_ids = my_subjects.values_list('id', flat=True)
    total_questions = Question.objects.filter(subject__in=my_subject_ids).count()
    
    # 4. Count active/upcoming exams
    now = timezone.now()
    active_exams_count = my_exams.filter(end_time__gte=now).count()

    context = {
        'subjects': my_subjects,
        'exams': my_exams,
        'total_questions': total_questions,
        'active_exams_count': active_exams_count,
    }
    return render(request, 'dashboard/faculty_dashboard.html', context)

# Student Account and Dashboards 

@login_required
@student_required
def student_dashboard(request):
    now = timezone.now()

    # The threshold for when an exam becomes "Active" (Lobby opens 20 mins early)
    lobby_threshold = now + timedelta(minutes=20)

    # 1. Find exams the student has already completed
    attempted_exam_ids = StudentExam.objects.filter(
        student=request.user, 
        status='submitted'
    ).values_list('exam_id', flat=True)

    # 2. Active Exams: Lobby is open (start_time is within the next 20 mins or past) AND exam hasn't ended
    active_exams = Exam.objects.filter(
        start_time__lte=lobby_threshold, 
        end_time__gte=now
    ).exclude(id__in=attempted_exam_ids).order_by('end_time')

    # 3. Upcoming Exams: Lobby hasn't opened yet (start_time is more than 20 mins away)
    upcoming_exams = Exam.objects.filter(
        start_time__gt=lobby_threshold
    ).order_by('start_time')

    # 4. Past Results
    past_results = StudentExam.objects.filter(
        student=request.user, 
        status='submitted'
    ).order_by('-completed_at')

    context = {
        'active_exams': active_exams,
        'upcoming_exams': upcoming_exams,
        'past_results': past_results,
    }
    return render(request, 'dashboard/student_dashboard.html', context)




@login_required
@admin_required
def manage_users(request):
    search_q = request.GET.get('q', '')
    active_tab = request.GET.get('tab', 'students') # Default to students tab

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_user':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role = request.POST.get('role')

            # 1. Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" is already taken.')
            else:
                # 2. Securely create the user (this hashes the password!)
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # 3. Assign the custom role and save
                user.role = role
                user.save()
                
                messages.success(request, f'{role.capitalize()} "{username}" registered successfully!')
            
            # Keep them on the tab of the role they just created
            return redirect(f'/accounts/admin-dashboard/users/?tab={role}s')

    # Fetch Data & Apply Search Filters
    users = User.objects.all().order_by('-date_joined') # Newest first
    if search_q:
        users = users.filter(Q(username__icontains=search_q) | Q(email__icontains=search_q))

    # Split the querysets for the tabs
    students = users.filter(role='student')
    faculty = users.filter(role='faculty')

    context = {
        'students': students,
        'faculty': faculty,
        'search_q': search_q,
        'active_tab': active_tab,
    }
    # Ensure this path matches where you save the HTML file!
    return render(request, 'accounts/manage_users.html', context)